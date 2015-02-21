/* printer.c */
/* justin domingue - 260588454 */

#include <stdio.h>
#include <stdlib.h>   /* required for rand() */
#include <unistd.h>   /* required for sleep() */
#include <pthread.h>

#define TRUE 1
#define FALSE 0
#define CONSUMER_INTERVAL 5   /* client thread generate requests at a interval 5 sec */

/* TYPEDEF DEFINITION*/
typedef int buffer_item;  /* buffer_item is now the same as int */

/* SHARED */
pthread_mutex_t mutex;    /* mutex lock */

pthread_cond_t empty = PTHREAD_COND_INITIALIZER,   /* create a condition variable statically */
               fill  = PTHREAD_COND_INITIALIZER;

buffer_item *buffer;      /* shared buffer implemented as a circular array */
int in = 0,
    out = 0;
int buffer_size = 0;

pthread_t tid;           /* Thread ID */
pthread_attr_t attr;      /* thread attributes */

/* FUNCTION PROTOTYPES */
int insert_item(buffer_item item);    /* insert item into buffer */
int remove_item(buffer_item *item);   /* remove an object from buffer */

void *producer(void *param);
void *consumer(void *param);

/* MAIN FUNCTION */
int main(int argc, const char *argv[])
{
  int i;	/* loop counter */

  /* Verify command-line arguments */
  if (argc != 4) {
    printf("Usage: %s C P B\nC - number of clients\nP - number of printers\nB - buffer size\n", argv[0]);
    return -1;
  }

  /* Initialize command-line options */
  int n_clients = atoi(argv[1]);
  int n_printers = atoi(argv[2]);
  buffer_size = atoi(argv[3]);

  /* Initialize buffer */
  buffer = (int*)malloc(buffer_size * sizeof(buffer_item));   /* allocate memory for the buffer array */
  if (buffer == NULL) {
    printf("Error allocating memory for the buffer.\n");
    return -1;
  }

  /* Initialize synchronization structures */
  pthread_mutex_init(&mutex, NULL); /* initialize mutex lock */
  pthread_attr_init(&attr);         /* initialize default attributes */

  /* Create producer thread(s) */
  for (i = 0; i < n_clients; ++i)
    pthread_create(&tid, &attr, producer, (void *) &i);  /* create a new thread */

  /* Create consumer thread(s) */
  for (i = 0; i < n_printers; ++i)
    pthread_create(&tid, &attr, consumer, (void *) &i);  /* create a new thread */

  /* Sleep */
  sleep(1000);

  /* Exit */
  return 0;
}

void *producer(void *param)
{
  int producer_number = *((int*)param);  /* save param to an int */
  int pos_in_buffer;                    /* where next_produced was inserted inside buffer */

  buffer_item next_produced;      /* create a new item */

  while(TRUE) {
    int random= rand() % 10 + 1;  /* Generate random number between 1 and 10*/

    next_produced = random;       /* put number in page to print inside next_produced */

    /* CRITICAL SECTION */
    pthread_mutex_lock(&mutex);   /* acquire mutex lock */

    if ((in + 1) % buffer_size == out) {
      printf("Client %d has %d pages to print, buffer full, sleeps\n", producer_number, next_produced);
      pthread_cond_wait(&empty, &mutex);
      pos_in_buffer = insert_item(next_produced);
      printf("Client %d wakes up, put request in Buffer[%d]\n", producer_number, pos_in_buffer);
    } else {
      pos_in_buffer = insert_item(next_produced);
      printf("Client %d has %d pages to print, puts request in Buffer[%d]\n", producer_number, next_produced, pos_in_buffer);
    }

    pthread_cond_signal(&fill);
    pthread_mutex_unlock(&mutex); /* release mutex lock */
    /* END CRITICAL SECTION */

    sleep(CONSUMER_INTERVAL);     /* Sleep before generating new print job */
  }
}

void *consumer(void *param)
{
  int consumer_number = *((int*)param);
  int pos_in_buffer;

  buffer_item next_consumed;

  while (TRUE) {

    /* CRITICAL SECTION */
    pthread_mutex_lock(&mutex); /* acquire the mutex lock */

    if(in == out) {
      printf("No request in buffer, Printer %d sleeps\n", consumer_number);
      pthread_cond_wait(&fill, &mutex);
    }

    /* remove an item and save the buffer */
    pos_in_buffer = remove_item(&next_consumed);

    pthread_cond_signal(&empty);  /* signal */
    pthread_mutex_unlock(&mutex); /* release the mutex lock */
    /* END - CRITICAL SECTION */

    /* Start printing */
    printf("Printer %d starts printing %d pages from Buffer[%d]\n", consumer_number, next_consumed, pos_in_buffer);

    /* Sleep for a random period of time */
    sleep(next_consumed);

    /* Finish printing */
    printf("Printer %d finishes printing %d pages from Buffer[%d]\n", consumer_number, next_consumed, pos_in_buffer);
  }
}

int insert_item(buffer_item item)
{
  /* If buffer is not full, add item and update counter */
  buffer[in] = item;
  in = (in + 1) % buffer_size;
  return in;
}

int remove_item(buffer_item *item)
{
  *item = buffer[out];  /* remove item from buffer into *item */
  out = (out + 1) % buffer_size;
  return out;               /* return place where item was extracted */
}
