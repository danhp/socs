// User level threading library.
// Written by Daniel Pham
// 260 526 252

#define _XOPEN_SOURCE 600

#include <stdio.h>
#include <stdlib.h>
#include <ucontext.h>

#define TRUE 1
#define FALSE 0
#define THREAD_NAME_LEN 50
#define LIST_LEN 5

//Data Structures
// Run Queue, Wait Queues
// Control Block Table

void* stack;

//Index each entry in an array.
typedef struct _mythread_control_block{
    ucontext_t context;
    char thread_name[THREAD_NAME_LEN];
    int thread_id;
} mythread_control_block;

typedef struct _semaphore{
    int value;
    // int id;
    //list
} semaphore;

int mythread_init(){

    return 0;
}

int mythread_create(char *threadName, void (*threadfunc)(), int stacksize){
    //Allocate memory to the stack
    stack = malloc(stacksize);
    if (stack == 0){
        perror("malloc: could not allocated the stack");
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

int create_semaphore(int value){

    return 0;
}

//Implemented with a semaphore table or a linked list.
void semaphore_wait(int semaphore){

}

void semaphore_signal(int semaphore){

}

void destroy_semaphore(int semaphore){

}

void mythread_state(){

}

int main(){

    return 0;
}
