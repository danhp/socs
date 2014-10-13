// Printer Spooler
// Daniel Pham
// 260 526 252

#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <semaphore.h>
#include <pthread.h>

#define TRUE 1
#define FALSE 0
#define PRODUCTION_INTERVAL 5

typedef int bufferItem;

sem_t mutex;
sem_t full;
sem_t empty;

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

    //Init the semaphores
    sem_init(&mutex, 0, 1);
    sem_init(&full, 0, 0);
    sem_init(&empty, 0, bufferSize);

    buffer = (int*) malloc(bufferSize * sizeof(bufferItem));
    if (buffer == NULL){
        printf("Error allocating memory to the buffer\n");
        return -1;
    }

    //Init the thread Atributes
    pthread_attr_init(&tAttr);

    //Create Printer threads
    pthread_t printerThread[numPrinters];
    for(int i = 1; i <= numPrinters; ++i){
        pthread_create(&printerThread[i - 1], 0, printer, (void *) i);
    }

    //Create Client threads
    pthread_t clientThread[numClients];
    for(int i = 1; i <= numClients; ++i){
        pthread_create(&clientThread[i - 1], 0, client, (void *)i);
    }

    sleep(20);
    return(0);
}

void *client(void *param){
    int clientId = (int) param;
    int indexBuffer;

    bufferItem nextJob;

    while(TRUE){
        nextJob = rand() % 10 + 1;

        //Critical Section
        sem_wait(&mutex);

        if((in + 1) % bufferSize == out){
            printf("Client %d has %d pages to print, buffer full, sleeps\n", clientId, nextJob);
            sem_wait(&empty);
            indexBuffer = insertJob(nextJob);
            printf("Client %d wakes up, put request in Buffer[%d]\n", clientId, indexBuffer);
        } else {
            sem_wait(&empty);
            indexBuffer = insertJob(nextJob);
            printf("Client %d has %d pages to print, puts request in Buffer[%d]\n", clientId, nextJob, indexBuffer);
        }

        sem_post(&mutex);
        sem_post(&full);
        //End Crictical section

        sleep(PRODUCTION_INTERVAL);
    }
}

void *printer(void *param){
    int printerId = (int) param;
    int indexBuffer;

    bufferItem nextJob;

    while(TRUE){
        //Critical Section
        sem_wait(&mutex);

        if(in == out){
            printf("No request in buffer, Printer %d sleeps\n", printerId);
            sem_wait(&full);
        }

        indexBuffer = removeJob(&nextJob);

        sem_post(&mutex);
        sem_post(&empty);
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
