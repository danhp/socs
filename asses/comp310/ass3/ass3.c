// User level threading library.
// Written by Daniel Pham
// 260 526 252

#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <ucontext.h>
#include <slack/list.h>

#define TRUE 1
#define FALSE 0
#define THREAD_NAME_LEN 50

//Data Structures
// Run Queue, Wait Queues
// Control Block Table

void* stack;

//Index each entry in an array.
typedef struct mythread_control_block{
    ucontext_t context;
    char thread_name[THREAD_NAME_LEN];
    int thread_id;
} mythread_control_block;

typedef struct semaphore{
    int id;
    int count;
    struct semaphore *next;
    struct listElement *nextElement;
} semaphore;

typedef struct list_element{
    char thread_name[THREAD_NAME_LEN];
    struct listElement *next;
} list_element;

semaphore *firstSemaphore = NULL;

int mythread_init(){

    return 0;
}

int mythread_create(char *threadName, void (*threadfunc)(), int stacksize){
    //Allocate memory to the stack
    stack = malloc(stacksize);
    if (stack == 0){
        perror("malloc: could not allocate the stack");
        return -1;
    }

    return 0;
}

void mythread_exit(){

}

void runthreads(){

}

void set_quantum_size(int quantum){

}

int create_semaphore(int semValue){
    semaphore *s = firstSemaphore;
    semaphore *newSemaphore = (semaphore*)malloc(sizeof(semaphore));

    //Init the new semaphore
    newSemaphore->count = semValue;
    newSemaphore->nextElement = NULL;

    if (firstSemaphore == NULL){
        firstSemaphore = newSemaphore;
    } else {
        while (s->next != NULL){
            s = s->next;
        }
        newSemaphore->id = s->id + 1;
        s->next = newSemaphore;
    }

    return newSemaphore->id;
}

void semaphore_wait(int semId){

}

void semaphore_signal(int semId){

}

void destroy_semaphore(int semId){
    semaphore *currentSem = firstSemaphore;
    semaphore *previousSem = NULL;

    while (currentSem != NULL){
        if (currentSem->id == semId){
            break;
        } else {
            previousSem = currentSem;
            currentSem = currentSem->next;
        }
    }

    if (previousSem != NULL){
        previousSem->next = currentSem->next;
    } else {
        firstSemaphore = currentSem->next;
    }

    free(currentSem);
}

void mythread_state(){

}

int main(){
    create_semaphore(3);
    return 0;
}
