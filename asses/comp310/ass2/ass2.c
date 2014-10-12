// Printer Spooler
// Daniel Pham
// 260 526 252

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>

#define TRUE 1
#define FALSE 0
#define PRODUCTION_INTERVAL 5

typedef int bufferItem;

pthread_mutex_t mutex;

pthread_cond_t empty = PTHREAD_COND_INITIALIZER;
pthread_cond_t fill = PTHREAD_COND_INITIALIZER;

bufferItem *buffer;
int bufferSize;
int in = 0;
int out = 0;

pthread_t tId;
pthread_attr_t tAttr;

//Function Prototypes
void *client(void *param);
void *printer(void *param);
int insertJob(bufferItem item);
int removeJob(bufferItem *item);

int main(int argc, const char *argv[]){
    if (argc != 4) {
        printf("Usage: %s C P B\nC - number of clients\nP - number of printers\nB - buffer size\n", argv[0]);
        return -1;
    }

    //Init the arguments
    int numClients = atoi(argv[1]);
    int numPrinters = atoi(argv[2]);
    bufferSize = atoi(argv[3]);

    buffer = (int*) malloc(bufferSize * sizeof(bufferItem));
    if (buffer == NULL){
        printf("Error allocating memory to the buffer\n");
        return -1;
    }

    //Init the sync structures
    pthread_mutex_init(&mutex, NULL);
    pthread_attr_init(&tAttr);

    //Create Printer threads
    for(int i = 0; i < numPrinters; i++){
        pthread_create(&tId, &tAttr, printer, (void *) &i);
    }

    //Create Client threadsß
    for(int i = 0; i < numClients; i++){
        pthread_create(&tId, &tAttr, client, (void *) &i);
    }

    sleep(120);
    return(0);
}

void *client(void *param){
    int clientId = *((int*)param);
    int indexBuffer;

    bufferItem nextJob;

    while(TRUE){
        nextJob = rand() % 10 + 1;

        //Critical Section
        pthread_mutex_lock(&mutex);

        if((in + 1) % bufferSize == out){
            printf("Client %d has %d pages to print, buffer full, sleeps\n", clientId, nextJob);
            pthread_cond_wait(&empty, &mutex);
            indexBuffer = insertJob(nextJob);
            printf("Client %d wakes up, put request in Buffer[%d]\n", clientId, indexBuffer);
        } else {
            indexBuffer = insertJob(nextJob);
            printf("Client %d has %d pages to print, puts request in Buffer[%d]\n", clientId, nextJob, indexBuffer);
        }

        pthread_cond_signal(&fill);
        pthread_mutex_unlock(&mutex);
        //End Crictical section

        sleep(PRODUCTION_INTERVAL);
    }
}

void *printer(void *param){
    int printerId = *((int*)param);
    int indexBuffer;

    bufferItem nextJob;

    while(TRUE){
        //Critical Section
        pthread_mutex_lock(&mutex);

        if(in == out){
            printf("No request in buffer, Printer %d sleeps\n", printerId);
            pthread_cond_wait(&fill, &mutex);
        }

        indexBuffer = removeJob(&nextJob);

        pthread_cond_signal(&empty);
        pthread_mutex_unlock(&mutex);
        //End Critical section

        printf("Printer %d starts printing %d pages from Buffer[%d]\n", printerId, nextJob, indexBuffer);
        sleep(nextJob);
        printf("Printer %d finished printing %d pages from Buffer[%d]\n", printerId, nextJob, indexBuffer);
    }

}

int insertJob(bufferItem item){
    buffer[in] = item;
    in = (in + 1) % bufferSize;
    return in;
}

int removeJob(bufferItem *item){
    *item = buffer[out];
    out = (out + 1) % bufferSize;
    return out;
}
