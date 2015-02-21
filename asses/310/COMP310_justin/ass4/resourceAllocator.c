//Harry Simmonds - 260502863
/* resourceAllocator.c */


#include <stdio.h>
#include <stdlib.h>     /*use for rand() generator */
#include <pthread.h>
#include <time.h>       /*to count simulation time */
#include <unistd.h>

#define true 1          /* define true/false */
#define false 0

#define INTERVAL 2      /*value to which to check for deadlock (deadlock detection( */
#define SEED 1395346165/*SEED value to track random generations*/

pthread_mutex_t mutex;  /*mutex lock */
pthread_attr_t attr;    /*set of thread attributes */

pthread_cond_t notSafe = PTHREAD_COND_INITIALIZER; /*condition variable for threads to wait until resources released */

/* shared variables */
char strategy;                                  //to find what user the strategy wants
int numProcesses,resourceTypes,simTime;         //arguments in main

/* declare data structures for banker's algorithm & simulation time*/
int *available, *range, **max, **allocation, **need, **request, *runningTimes;

/* delcared functions */
int safetyAlg(int n, int m);            //determines whether state is safe
int resourceAllocator(int processIndex, int n, int m);  //allocates resources in AVOIDANCE
int checkRequest(int processIndex);     //checks if there are enough resources to allocate
void detector();                        //detecs deadlocks


void allocateResources(int processIndex, int m);        //changes state to allocate
void releaseResources(int processIndex, int m);         //changes state to release

void genRequest(int processIndex); //generates request

void *process(void *param);     //thread method

int avoidance(int processIndex);        //various strategies
int detection(int processIndex);

void usage(const char *arg[]) { //man- page of program
    printf("Usage: %s S N ST T R\n S - Deadlock Strategy (a = avoidance : d = detection)\n N - Number of Processes\n ST - simulated time\n T - number of resource Types\n R - range of resource types\t NOTE: there should be a range for each given resource type\n\t example: T = 3, then R = 3 6 4\n", arg[0]);
           
}

int main(int argc, const char *argv[]) {
    
    srand(SEED); //seed time so rand() produces same results
    
    
    if (argc < 6) { //if not enough arguments provided
        usage(argv);
        return -1;
    }
    
    //*argv[] input = deadlock strategy, num processes, simulated time,type of res, range of res types,
    strategy = argv[1][0];
    numProcesses = atoi(argv[2]);
    simTime = atoi(argv[3]);
    resourceTypes = atoi(argv[4]);  //types translate to typical values of A, B , C.... etc
    
    //check that there are range values for every resource type
    if ((argc != (5 + resourceTypes))) {
        usage(argv);
        return -1;
    }
    
    //notify user what strategy
    if (strategy == 'a') {
        printf("\n---- Using Deadlock Avoidance ----\n\n");
    }
    else {
        printf("\n---- Using Deadlock Detection ----\n\n");
    }
    
    /*initialize thread components and pthread mutex */
    pthread_mutex_init(&mutex,NULL);
    pthread_attr_init(&attr);
    pthread_t tid[numProcesses];
    
    //init data structures for Banker's algorithm
    
    int  n = numProcesses;
    int  m = resourceTypes;
    
    int i, k; //iterator indices
    
    range = (int *)malloc(m*sizeof(int));           //range used to find initial readily available resources
    available = (int *)malloc(m*sizeof(int));       //current available resources
    max = (int **)malloc(n*sizeof(int*));           //init to random number generator for each process between with max = available[i]
    allocation = (int **)malloc(n*sizeof(int*));    //init to 0 as no alloc.
    need = (int **)malloc(n*sizeof(int*));          //what each process needs for resource allocation
    request = (int **)malloc(n*sizeof(int*));       //requests of processes
    runningTimes = (int *)malloc(n*sizeof(int));    //the collective runningTime of each process
    
    /* INIT AND ALLOCATE DATA STRUCTURES */
    for (i = 0; i < m; i++) {
        available[i] = atoi(argv[5 + i]); //init available array
        runningTimes[i] = 0;            //init runningTimes of each process
        range[i] = available[i];
    }
    
    for (i = 0; i < n; i++) {
        max[i] = (int *)malloc(m*sizeof(int));
        allocation[i] =(int *)malloc(m*sizeof(int));
        need[i] = (int *)malloc(m*sizeof(int));
        request[i] = (int *)malloc(m*sizeof(int));
    }
    
    for (i = 0; i < n; i++) {
        for (k = 0; k < m; k++) {
            max[i][k] = rand() % (available[k] + 1);
            allocation[i][k] = 0;
            need[i][k] = max[i][k];
            request[i][k] = 0;
        }
    }
    
    printf("\tNOTE: succesfully initialized data\n\n");
    
    int j;
    clock_t current_time = 0; //initialize clock
    
    printf("-----Simulation Starting-----\n");
    
    current_time = clock(); //start simulation time
    
    //create threads
    for (j = 0; j < numProcesses; j++) {
        pthread_create(&tid[j],&attr,process,(void *)j);
    }
    
    //continusouly check whether beyond simulation time - then exit
    while (clock() < (current_time + simTime*CLOCKS_PER_SEC)) {//run until simulation time is over
        if (strategy == 'd') { //ensure to use detection periodically
            
            //if it is on an interval of 2 - use detector
            if (((clock()/CLOCKS_PER_SEC) % INTERVAL) == 0) {
                detector();
            }
        }
        // else using avoidance and no detector() needed
    }
    
    printf("----- Simulation END ---------\n ");

    int sum = 0;
    //calculate sum of simulations
    for (i = 0; i < numProcesses; i++) {
        sum += runningTimes[i];
    }
    printf("The sum of runningTimes : %d\n", sum);
    
    exit(0); //end program
}


//safety algorithm for both strategies - determines whether it is in deadlock OR whether is suitable for safe state
int safetyAlg(int n, int m) {
    //n = numProcesses
    //m = resourceTypes
    int strat;
    if (strategy == 'a') strat = 1;  // 1 = avoidance, 0 = detection
    else strat = 0;
    
    int work[m];
    int finish[n];
    
    int i, k;       //iterators
    
    /*------------ STEP 1: initialize --------------*/
    
    //init work array
    for (i = 0; i < m; i++) work[i] = available[i];
    
    if (strat) { //strategy is avoidance
        //init finish array to false for processes
        for (i = 0; i < n; i++) finish[i] = false;
    }
    else { //strategy is detection
        int sum;
        for (i = 0; i < n; i++) {
            sum = 0;
            for (k = 0; k < m; k++) {
                sum += allocation[i][k];
            }
            if (sum == 0) finish[i] = false;
            else finish[i] = true;
        }
    }
    
    /*------------- STEP 2: find index -------------*/

    int indicator1, indicator2;
    
    //find suitable index i
step2:
    for (i = 0; i < n; i++) {
        if (finish[i] == false) {
            indicator1 = true;
            indicator2 = true;
            
            for (k = 0; k < m; k++) {
                if (need[i][k] > work[k]) indicator1 = false;
                if (request[i][k] > work[k]) indicator2 = false;
            }
            /* -------------- STEP 3 : update sub-states ------------ */
            if ((strat && indicator1) || (!(strat) && indicator2)) {
                for (k = 0; k < m; k++) {
                    work[k] = work[k] + allocation[i][k];
                }
                finish[i] = true;
                goto step2;     //repeat step 2
                
            }
        }
    }
    /* ------------ STEP 4: Determine safe state ----------- */
    for (i = 0; i < n; i++) {
        if (finish[i] != true) {
            printf("\n\tDEADLOCK DETECTED - denied request\n\n");
            return i;       //return the processIndex to kill (for deadlock detection)
        }
    }
    return -1; //state is safe
    
}

//allocates resources for banker's algorithm (AVOIDANCE)
int resourceAllocator(int processIndex, int n, int m) {
    int k;
    int modifier;
    int indicator = true;
    for (k = 0; k < m; k++) {
        if (request[processIndex][k] > need[processIndex][k]) indicator = false;
    }
    if (indicator == false) {
        printf("\n\n\tError - process has requested maximum claim\n\n");
        return 0; //0 = error code
    }
    else {
        for (k = 0; k < m; k++) {
            if (request[processIndex][k] > available[k]) indicator = false;
        }
        if (indicator == false) return 0;//process P(i) must wait no resources available
        
        
        //modify the states
        allocateResources(processIndex, m);
        
        if (safetyAlg(n,m) == -1) return 1; //state is safe - allocated resources
        else { //reverse state and state is unsafe
            for (k = 0; k < m; k++) {
                modifier = request[processIndex][k];
                
                available[k] = available[k] + modifier;
                allocation[processIndex][k] = allocation[processIndex][k] - modifier;
                need[processIndex][k] = need[processIndex][k] + modifier;
                
            }
            return 0; //state is unsafe, process must wait
        }
    }
}


//change state -> allocate resources
void allocateResources(int processIndex, int m) {
    int modifier;
    int k; //iterator
    for (k = 0; k < m; k++) {
        modifier = request[processIndex][k];
        
        available[k] = available[k] - modifier;
        allocation[processIndex][k] = allocation[processIndex][k] + modifier;
        need[processIndex][k] = need[processIndex][k] - modifier;
    }
    
    
}

//change state -> release resources
void releaseResources(int processIndex, int m) {
    int toRelease;
    int k; //iterator
    for (k = 0; k < m; k++) {
        if (request[processIndex][k] != 0) {
            toRelease = rand() % request[processIndex][k];
        }
        else toRelease = 0;
        
        request[processIndex][k] -= toRelease;
        available[k] += toRelease;
        allocation[processIndex][k] -= toRelease;
        need[processIndex][k] += toRelease;
    }
}

//check if there are enough resources for specific request
int checkRequest(int processIndex) {
    int i; //iterator
    for (i = 0; i < resourceTypes; i++) {
        if (request[processIndex][i] > available[i]) return 0;  //request denied
        
    }
    return 1; //request can be made
}


//initialize thread
void *process(void *param) {
    const int processIndex = (int)param; //set process number
    
    while (true) {
        int timeRequest = rand() % 10 + 1; //generate random number to request resource;
        int processResources = rand() % 10 + 1; //generate random number to hold resource;
        
        sleep(timeRequest); //sleep for random number of time before making request
        
        if (strategy == 'a') { //if strategy is avoidance
            avoidance(processIndex);
        }
        else {          //if strategy is detection
            detection(processIndex);
        }
        printf("Process %d has been ALLOCATED resources\n", processIndex);
        
        //resources have been claimed, simulate processing resources
        sleep(processResources);
        runningTimes[processIndex] += processResources; //find running time of active processsing
        
        //request more/ release resources
        int option; //variable to decide whether we request more resources or release
        
        option = rand() % 2;
        if (option == 0) { //then we release resources
            printf("Process %d RELEASING resources\n", processIndex);
            releaseResources(processIndex, resourceTypes);
            pthread_cond_broadcast(&notSafe); //signal to waiting processes that resources have been released
        }
        else printf("Process %d HOLDING resources\n", processIndex);
        //else continue through loop to request more
    }
    return NULL;
}

//Deadlock Avoidance
int avoidance(int processIndex) {
    int currentState;
    int safe = false;
    clock_t ctime = 0;
    int time = 0;
    
    pthread_mutex_lock(&mutex);  /*acquire mutex lock */
    
    /*make random resource request */
    printf("Process %d generating request\n", processIndex);
    genRequest(processIndex);
    
    while (!safe) { //keep attempting to get resources until attempt successful
        
        /* determine if state is safe and allocate resources if so */
        currentState = resourceAllocator(processIndex, numProcesses, resourceTypes);
        if (currentState == 0) { /*state is notsafe - must wait */
            printf("Process %d waiting on request\n", processIndex);
            ctime = clock();
            pthread_cond_wait(&notSafe,&mutex); //wait until resources are released
            time = (int)((clock() - ctime)/CLOCKS_PER_SEC);
            printf("Process %d waited %d seconds to get resources\n", processIndex, time);
            
            safe = false;
        }
        else safe = true;
    }
    pthread_mutex_unlock(&mutex); /*release mutex lock */
    
    //resources have been claimed
    return 1;
}


//Deadlock Detection - USED FOR DETECTION STRATEGY
int detection(int processIndex) {
    int check;
    int safe = false;
    clock_t ctime = 0;
    int time;
    
    pthread_mutex_lock(&mutex); /*acquire mutex lock */
    
    /* make random resource request*/
    printf("Process %d generating request\n", processIndex);
    genRequest(processIndex);
    
    while (!safe) { //loop until valid request
        check = checkRequest(processIndex); //check if there are enough resources to provide for request
        
        if (!check) { //request can't be made
            printf("Process %d waiting on request\n", processIndex);
            ctime = clock();
            pthread_cond_wait(&notSafe,&mutex); //wait until signaled
            time = (int)((clock() - ctime)/CLOCKS_PER_SEC);
            printf("Process %d waited %d seconds to get resources", processIndex, time);
            
            safe = false;
        }
        else safe = true;
    }
    //allocate resources
    allocateResources(processIndex, resourceTypes);
    
    pthread_mutex_unlock(&mutex); /*release mutex lock */
    
    return 1;
}


//USED TO DETECT DEADLOCKS - runs safety Algorithm
void detector() {
    pthread_mutex_lock(&mutex);
    
    int processIndex;
    
    processIndex = safetyAlg(numProcesses, resourceTypes); //check whether deadlock has occured
    
    if (processIndex >= 0) { //deadlock has occured, kill process - release all resources
        printf("\n\tDeadlock has occured, killing process %d\n", processIndex);
        int i, modifier;
        printf("\tReleasing all resources: process %d\n\n", processIndex);
        for (i = 0; i < resourceTypes; i++) {
            modifier = request[processIndex][i];
            request[processIndex][i] = 0;
            available[i] += modifier;
            allocation[processIndex][i] = 0;
        }
        //reset runningTime to 0
        runningTimes[processIndex] = 0;
        pthread_cond_broadcast(&notSafe); //signal that resources were released
    }
    pthread_mutex_unlock(&mutex);
}

//generates random request
void GenRequest(int processIndex) {
    //print();
    int i;
    for (i = 0; i < resourceTypes; i++) {
        if (strategy == 'a') { //if avoidance bound by need
            if (need[processIndex][i] != 0) {
                request[processIndex][i] = rand() % (need[processIndex][i] + 1); //make sure random number does not exceed need
            }
            else request[processIndex][i] = 0;
        }
        else request[processIndex][i] = rand() % (range[i] + 1); //get any random number within max available resources- detection
    }
}

//END OF CODE
