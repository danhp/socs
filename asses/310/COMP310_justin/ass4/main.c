/* simulation.c - Resource allocator
 * justin domingue - 260588454
 * 
 * Usage: {{{
 *  simulation strategy time number_of_customers number_of_resources
 *    strategy : strategy to use for the simulation
 *               0 - deadlocks avoidance
 *               1 - detection algorithm
 *    time : amount of time to simulate
 *    number_of_customers : number of customers
 *    number_of_each_types : number of resources for each type
 * }}}
 *
 * Workflow: {{{
 *
 * _main_
 *  - create threads to simulate different "customers"
 *  - run threads until end of simulation time
 *  - find total sum of runtime - print
 *
 * _threads_ 
 *  - come up with resource request
 *  - submit to resource allocator
 *  A receive resource
 *  - save time
 *  - run for some time
 *  - either
 *      - release resource
 *      - request more
 *  - save time
 *  B wait on condition variable
 *    - wait
 *    - on signal, go to A
 *
 * _allocator_
 *  - if avoidance
 *    allocate request if no danger of deadlock
 *  - if detection
 *    allocate resource if resource available
 *
 * }}}
 */

#include <stdio.h>
#include <stdlib.h>   /* for rand() */
#include <unistd.h> 
#include <pthread.h>  
#include <time.h>     /* for time() and clock() */

#define DETECTION_FREQUENCY 5 /* detection interval */
#define SEED 1395346212       /* seed value for rand() */

/* SHARED VARIABLES */
pthread_mutex_t mutex;      /* mutex lock */
pthread_cond_t available = PTHREAD_COND_INITIALIZER;  /* condition variable */

pthread_t tid;  
pthread_attr_t attr;

int strategy; // strategy being used for the simulation
int *times;   // Global array to store runtime of each customer

// in the detection scheme, when a deadlock is detected, the customer's time is reset to 0
// latestTimes hold the run time of the customer's last job so that if a deadlock is detected,
// only that job's time is reset and the other jobs are still running
int *latestTimes; 
int numberOfCustomers;  // number of customers (processes)  as declared at the command-line
int numberOfResources;  // number of resources

/* For Banker's Algorithm - as defined in the textbook */
int **allocated;
int **maximum;
int **need;
int **request;
int *avail;
int *completed;

/* FUNCTION PROTOTYPES */
void *customer(void *param);   // Simulates a customer
int request_resources(int customer);
int release_resources(int customer);
int safetyAlgorithm();
int resourceRequestAlgorithm(int customer_num);
int detection();

/* Useful functions for debugging */
void printResources()
{
  int i, j;
  for (i = 0;i<numberOfCustomers ;i++ ) {
    printf("Customer %d\n", i);
    for (j = 0;j<numberOfResources ;j++ ) {
      printf("\tResource %d", j);
      printf("\tAllocated %d, Maximum %d, Need %d, Available %d, Completed %d, Requested %d\n", allocated[i][j], maximum[i][j], need[i][j], avail[j], completed[i], request[i][j]);
    }
  }
}

int main(int argc, char *argv[])
{
  if (argc < 5) {
    printf("Usage: simulation strategy time number_of_customers number_of_resources\n");
    exit(-1);
  }

  /* Initialize SEED to always get the same sequence of random integers */
  srand(SEED);

  /* Initialize variables */
  int i, j, val, totalTime = 0;

  // Extract arguments from command-line
  strategy = atoi(argv[1]);             // strategy used in the simulation

  int timeToSimulate = atoi(argv[2]);                   // duration of the simulation
  times = (int *) malloc(atoi(argv[3]) * sizeof(int));  // initializr array of running time for each customers
  latestTimes = (int *) malloc(atoi(argv[3]) * sizeof(int));  // initializr array of running time for each customers

  numberOfCustomers = atoi(argv[3]);    // number of customers
  numberOfResources = atoi(argv[4]);    // number of resources

  /* Allocate memory */

  /* allocate first dimension */
  allocated = (int **) malloc(numberOfCustomers * sizeof(int *));
  maximum = (int **) malloc(numberOfCustomers * sizeof(int *));
  need = (int **) malloc(numberOfCustomers * sizeof(int *));
  request = (int **) malloc(numberOfCustomers * sizeof(int *));
  completed = (int *) malloc (numberOfCustomers * sizeof(int));
  avail = (int *) malloc (numberOfResources * sizeof(int));

  /* allocate second dimension */
  for(i = 0; i < numberOfCustomers; i++) {
    allocated[i] = (int *) malloc(numberOfResources * sizeof(int));
    maximum[i] = (int *) malloc(numberOfResources * sizeof(int));
    need[i] = (int *) malloc(numberOfResources * sizeof(int));
    request[i] = (int *) malloc(numberOfResources * sizeof(int));
  }

  /* Initialize data */

  /* set completed[] entries to false */
  for(i = 0; i < numberOfCustomers; i++) completed[i] = 0; // set flag to false

  /* ask use for avail matrix */
  printf("Enter number of AVAILABLE instances\n");
  for(i = 0; i < numberOfResources; i++) {
    printf("Resource %d : _\b", i);
    scanf("%d", &val);
    avail[i] = val;
  }

  /* ask user for maximum matrix */
  int choice;
  puts("Populate MAXIMUM matrix\n\t0) manually\n\t1) automatically");
  scanf("%d", &choice);

  if (choice == 0) {    // user populates maximum array
    printf("\nEnter MAXIMUM of instance of resources that a customer need.\n");
    for(i = 0; i < numberOfCustomers; i++) {
      printf("Customer %d\n ", i);
      for(j = 0; j < numberOfResources; j++) {
        printf("\tResources %d : _\b", j);
        scanf("%d", &val);
        if (val <= avail[j]) maximum[i][j] = val;
        else {
          printf("Not enough resources available.\n");
          j--;
        }
      }
    }
  } else {  // populate with random values
    puts("Populated maximum matrix automatically.");
    for (i = 0; i < numberOfCustomers; i++) {
      for (j = 0; j < numberOfResources; j++) {
        maximum[i][j] = rand() % (avail[j] + 1);
      }
    }
  }

  /* set allocated and need */
  for(i = 0; i < numberOfCustomers; i++) {
    for(j = 0; j < numberOfResources; j++) {
      allocated[i][j] = 0;
      need[i][j]      = maximum[i][j];
      request[i][j]   = 0;
    }
  }

  /* Initialize threads variables */
  pthread_mutex_init(&mutex, NULL);
  pthread_attr_init(&attr);

  puts("\n------- SIMULATION STARTS -------\n");

  /* Create threads */
  for (i = 0; i < numberOfCustomers; i++)
    pthread_create(&tid, &attr, customer, (void *) i); 

  /* Periodically run detection if needed */
  if (strategy == 1) {
    int accumulatedTime = 0;

    while (accumulatedTime < timeToSimulate) {
      sleep(DETECTION_FREQUENCY);     // wait 2 seconds before running detection
      detection();
      accumulatedTime += DETECTION_FREQUENCY; // update accumulated time
    }
  } else  // avoidance will check on every request so simply sleep for timeToSimulate
    sleep(timeToSimulate);

  puts("\n------- SIMULATION ENDS -------\n");

  totalTime = 0;  // reset totalTime

  /* Collect total sum of runtime */
  for (i = 0; i < numberOfCustomers; i++) {
    totalTime += times[i]; 
    totalTime += latestTimes[i];    // collect the last job's time as well
  }

  printf("Sum of runtime is %d\n", totalTime);

  /* RELEASE MEMORY */

  free(times);
  free(latestTimes);

  /* release second dimension */
  for(i = 0; i < numberOfCustomers; i++) {
    free(allocated[i]);
    free(maximum[i]);
    free(need[i]);
    free(request[i]);
  }

  /* release first dimension */
  free(allocated);
  free(maximum);
  free(need);
  free(request);
  free(completed);
  free(avail);

  return 0;
}

void *customer(void *param)
{
  int i;
  int customer_num = (int)param;  // Save customer number

  /* sleep for some time before making a request */
  sleep(rand() % 10);

  while(1) {
    printf("Customer %d is generating a request.\n", customer_num);

    /* Generate resource request bounded by customer's need */
    for (i = 0; i < numberOfResources; i++)
      request[customer_num][i] = rand() % (maximum[customer_num][i] - allocated[customer_num][i] + 1); 

    /* CRITICAL SECTION */
    pthread_mutex_lock(&mutex);    // acquire mutex lock

    int granted = request_resources(customer_num);    // submit resource to allocator

    // loop as long as the allocator has not granted the resource
    while (granted < 0) {
      printf("Customer %d is WAITING for resources to be released.\n", customer_num);

      // get current timestamp
      time_t t = time(NULL);

      // wait on the available condition variable
      pthread_cond_wait(&available, &mutex);  

      printf("Customer %d WAITED %d seconds. Requesting resources again.\n", customer_num, (int)(time(NULL)-t));

      // some resource got released, try again
      granted = request_resources(customer_num);           
    }

    // resources acquired - release mutex lock
    pthread_mutex_unlock(&mutex);     

    printf("Customer %d ACQUIRING resources.\n", customer_num);

    // consume resources for some time 
    int sleepingTime = rand() % 20;
    sleep(sleepingTime);

    // Compute the runtime for the customer
    latestTimes[customer_num] += sleepingTime;

    // generate random number (0 or 1) to decided whether the process will keep its resources are release them
    int keepResources = rand() % 2;

    if (keepResources == 0) {
      printf("Customer %d RELEASING its resources.\n", customer_num);

      // Release resource 
      release_resources(customer_num);

      // signal available lock
      pthread_cond_broadcast(&available);  

      // Remember that latestTimes holds the runtime of the customer's last job
      // Add that time into times
      
      times[customer_num] += latestTimes[customer_num];
      // Reset latestTimes for current customer to 0
      latestTimes[customer_num] = 0;

      // allow some time for the signal to broadcast to other customers 
      sleep(2);

    } else // Otherwise, request more - run the while loop again, but keep what the customer already has
      printf("Customer %d is KEEPING its resources.\n", customer_num);

  }
}

int request_resources(int customer_num)
{
  int i;

  if (strategy == 0) {    // banker
    // test if request will generate a deadlock
    if (resourceRequestAlgorithm(customer_num) == -1)
      return -1;
  } else {    // detection

    /* first check if enough resources are available to grant the request */
    for (i = 0; i < numberOfResources; i++)
      if (avail[i] < request[customer_num][i])
        return -1;

    /* Give resources without checking for deadlocks */
    /* the detection algorithm will run periodically */
    for (i = 0; i < numberOfResources; i++) {
      avail[i] -= request[customer_num][i];
      allocated[customer_num][i] += request[customer_num][i];
      need[customer_num][i] = maximum[customer_num][i] - allocated[customer_num][i] - request[customer_num][i];
    }

  }

  /* allocation was granted - return success */
  return 0;
}

int release_resources(int customer_num)
{
  int i;

  // Release resources
  for (i = 0; i < numberOfResources; i++) {
    allocated[customer_num][i] -= request[customer_num][i];
    need[customer_num][i] += request[customer_num][i];
    avail[i] += request[customer_num][i];
  }

  /* reset request matrix to 0 for customer_num */
  for (i = 0; i < numberOfResources; i++)
    request[customer_num][i] = 0;

  return 0;
}

int resourceRequestAlgorithm(int customer_num)
{
  int i;

  /* NOTE mutex lock was acquired by customer in customer() and will be released in customer() */

  /* RESOURCE-REQUEST ALGORITHM - adapted from the textbook's algorithm */

  /* Step 1 and 2 */
  for (i = 0; i < numberOfResources; i++) {
    // check if request is smaller than need and enough resource available
    if (request[customer_num][i] > need[customer_num][i] || request[customer_num][i] > avail[i])
      return -1;
  }

  /* Step 3 - pretend requested resources allocation */
  for (i = 0; i < numberOfResources; i++) {
    avail[i] -= request[customer_num][i];
    allocated[customer_num][i] += request[customer_num][i];
    need[customer_num][i] -= request[customer_num][i];
  }

  /* run safetyAlgorithm algorithm */
  if (safetyAlgorithm() != 0) {
    // not a safe state - restore old values
    for (i = 0; i < numberOfResources; i++) {
      avail[i] += request[customer_num][i];
      allocated[customer_num][i] -= request[customer_num][i];
      need[customer_num][i] += request[customer_num][i];
    }

    return -1;
  }

  return 0;
}

/* safety alogirhtm - adapted from textbook's algorithm */
int safetyAlgorithm()
{

  // loop and counter variables
  int i = 0, j = 0, k = 0;
  int indicator = 0;

  /* Step 1 */

  /* Initialize work to avail */
  int work[numberOfResources];
  for (i = 0; i < numberOfResources; i++) work[i] = avail[i];

  /* Reset completed[] */
  for(i = 0; i < numberOfCustomers; i++)
    completed[i] = 0; // set flag to false

  /* Steps 2-3 */

  /*find a suitable index i*/
step2:
  for (i = 0; i < numberOfCustomers; i++) {
    if (completed[i] == 0) {
      indicator = 0;  // reset indicator

      for (j = 0; j < numberOfResources; j++) {
        if (need[i][j] > work[j]) indicator = 1;
      }

      /* step 3 */
      if (indicator != 1) {
        for (k = 0; k < numberOfResources; k++) work[k] += allocated[i][k];
        completed[i] = 1;
        goto step2;
      }
    }
  }

  /* Step 4 - determine if the sytem is in sage state */
  for (i = 0; i < numberOfCustomers; i++) {
    if (completed[i] != 1) {
      printf("\n\tDEADLOCK DETECTED - denying allocation!\n\n");
      return -1;
    }
  }

  /* System is in safe state */
  return 0;

}

int detection()
{
  pthread_mutex_lock(&mutex); // acquire lock

  int i = 0, j = 0, indicator = 1;

  /* Step 1 */

  /* Initialize work to avail */
  int work[numberOfResources];
  for (i = 0; i < numberOfResources; i++)
    work[i] = avail[i];

  /* Reset completed[] */
  for(i = 0; i < numberOfCustomers; i++) {
    int sum = 0;

    /* Compute the sum of all allocated resources */
    for (j = 0; j < numberOfResources; j++) 
      sum += allocated[i][j];

    /* Set completed according to algorithm described in the textbook */
    if (sum == 0)
      completed[i] = 1; // set flag to true
    else
      completed[i] = 0; // set flag to false
  }

  /* Steps 2-3 */
  for (i = 0; i < numberOfCustomers; i++) {

    // find an index i such that completed[i] == 0
    if (completed[i] == 0) {

      // Check if request[i][j] < work[j] for all j, indicator remains truthy
      for (j = 0; j < numberOfResources; j++) 
        if (request[i][j] > work[j]) indicator = 0;

      // step 3 - only if indicator is true
      if (indicator) {
        for (j = 0; j < numberOfResources; j++) {
          work[j] = work[j] + allocated[i][j];
          completed[i] = 1;
        }
      }
    }
  }

    /* Step 4 of detection */
  for (i = 0; i < numberOfCustomers; i++) {
    if (completed[i] == 0)  { // system is in deadlock
      printf("\nDEADLOCK DETECTED - Releasing resources held by customer %d\n\n", i);

      // Release customer i from *all* its resources
      for (j = 0; j < numberOfResources; j++) {
        avail[j] += allocated[i][j];
        allocated[i][j] = 0;
        need[i][j] = maximum[i][j];
        request[i][j] = 0;
      }

      // Reset time to 0
      latestTimes[i] = 0;

      pthread_cond_signal(&available);
      
      // Released one process
      pthread_mutex_unlock(&mutex);
      return 0;
    }
  }

  pthread_mutex_unlock(&mutex);

  return 0;
}
