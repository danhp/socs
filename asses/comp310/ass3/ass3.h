



int mythread_create(char *threadName, void (*threadfunc)(), int stacksize);
void mythread_exit();
void runthreads();
void set_quantum_size(int quantum);
