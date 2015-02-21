// JUSTIN DOMINGUE
// 260588454

#include <stdio.h>  
#include <stdlib.h>
#include <sys/mman.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <signal.h>
#include <unistd.h>
#include <string.h>

#define STACK_BLOCK_SIZE 1
#define HEAP_BLOCK_SIZE  1024
#define START_DATA       0x08048000

extern char etext, edata, end; /* The symbols must have some type */

unsigned long int stackSize = 0,  /* stack and heap size retrieved from log file */
                  stackAddr = 0,
                  heapSize = 0,
                  heapAddr = 0,
                  mmapSize = 0,
                  mmapAddr = 0; 

void initializeLog()
{
  /* LOG FILE
   * Open log file and retrieve stack and heap size */
  FILE *f = fopen("size_log", "ab+");
  if (NULL == f) {
    perror("Opening file");
    exit(-1);
  }

  /* Parse the file 
   * what is awesome about fscanf is that if the pattern doesn't match,
   * it will leave stackSize and heapSize untouched, that is, 0
   * FILE FORMAT (CSV)
   *    STACK_SIZE,STACK_ADDR,HEAP_SIZE,HEAP_ADDR,MMAP_SIZE,MMAP_ADDR
   */
  fscanf(f, "%lx,%lx,%lx,%lx,%lx,%lx\n", &stackSize, &stackAddr, &heapSize, &heapAddr, &mmapSize, &mmapAddr);

  /* Close file */
  fclose(f);
}

/* findStackSize() : Find the stack segment size
 *  the program keeps track of the first 
 *  and last address of the stack
 */
void findStackSize()
{
  int *firstStackPointer = (int *) alloca(1);   // store the address of the first stack pointer
  int *lastStackPointer = firstStackPointer;    // store the address of the second stack pointer
  stackAddr = (int) firstStackPointer;          // first stack address

  stackSize = 1;    // Reinitialize stackSize - 1 because we allocate firstStackPointer 1 byte

  /* Open log file in write mode */
  FILE *f = fopen("size_log", "w");
  if (NULL == f) {
    perror("Opening log file");
    exit(EXIT_FAILURE);
  }

  printf("Please wait while I find the stack size of the object file.\n");
  printf("Note: the system will report a Segmentation Fault.\nNo worries. This is all good.\n");

  /* Allocate as much memory on the stack as possible */
  while(lastStackPointer != NULL) {
    fseek(f, 0, SEEK_SET);                                    // Point file pointer to the beginning of the file
    lastStackPointer = (int *) alloca(STACK_BLOCK_SIZE);      // allocate STACK_BLOCK_SIZE byte
    stackSize = stackSize + STACK_BLOCK_SIZE;                 // update experimental stack size
    fprintf(f, "%lx,%lx,%lx,%lx,%lx,%lx", stackSize, stackAddr, heapSize, heapAddr, mmapSize, mmapAddr);
  }

  fclose(f);
}

/* findHeapSize() : Find the heap segment size
 *  the program keeps track of the first 
 *  and last address of the heap
 */
void findHeapSize()
{
  int *firstHeapPointer = (int *) malloc(1);  // store the address of the first heap pointer
  int *lastHeapPointer = firstHeapPointer;    // store the address of the second heap pointer
  heapAddr = (int) firstHeapPointer;          // First heap address

  heapSize = 1;     // Reinitialize heap size

  /* Open log file in write mode */
  FILE *f = fopen("size_log", "w");
  if (NULL == f) {
    perror("Opening log file");
    exit(EXIT_FAILURE);
  }

  printf("Please wait while I find the heap size of the executable.\n");

  while(lastHeapPointer != NULL) {
    lastHeapPointer = (int *) malloc(HEAP_BLOCK_SIZE);      // allocate one byte
    fseek(f, 0, SEEK_SET);    // put file pointer to the beginning of the file
    heapSize = heapSize + HEAP_BLOCK_SIZE;
    fprintf(f, "%lx,%lx,%lx,%lx,%lx,%lx", stackSize, stackAddr, heapSize, heapAddr, mmapSize, mmapAddr);
  }

  fclose(f);
}

void findMMapSize(const char *filename)
{
  mmapSize = 0;

  int *fptr, *lptr;

  printf("Please wait while I find the memory map size of the executable.\n");

  // Open the file to map
  int fd = open(filename, O_RDONLY);
  if (fd < 0) {
    perror("Opening file");
    exit(EXIT_FAILURE);
  }

  /* Open log file in write mode */
  FILE *f = fopen("size_log", "w");
  if (NULL == f) {
    perror("Opening log file");
    exit(EXIT_FAILURE);
  }

  // Get the size of the file...
  struct stat filestat;

  if (fstat(fd, &filestat) == -1) 
    perror("Unable to get file size.");

  // Do a memory map of the file
  fptr = (int*)mmap(NULL, filestat.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
  lptr = fptr;
  mmapAddr = (int) fptr;

  while ((*lptr) > -1) {      // While mmap does not return -1 (er
    lptr = (int*)mmap(NULL, filestat.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    fseek(f, 0, SEEK_SET);
    mmapSize = mmapSize + filestat.st_size;
    fprintf(f, "%lx,%lx,%lx,%lx,%lx,%lx", stackSize, stackAddr, heapSize, heapAddr, mmapSize, mmapAddr);
  }

  fclose(f);

  return;
}

int main(int argc, const char *argv[])
{

  initializeLog();

  /* If 3 arguments were provided, there was a switch */
  if (argc == 2) {
    if (argv[1][1] == 'd') findHeapSize();            /* find heap size */
    if (argv[1][1] == 's') findStackSize();           /* find stack size */
    if (argv[1][1] == 'm') findMMapSize(argv[0]);     /* find memory map segment size */
    if (argv[1][1] == 'h')                            /* Usage */
      printf("Usage: %s [-d|-s|-m|-h]\n -d  Heap (dynamic) segment size\n -s  Stack segment size\n -m  Memory Map segment size\n -h  Help\n", argv[0]); /* find memory map segment size */
    return 0;
  }

  /* Check if user has run the program with the switches -d, -s and -m
   * (if not, the sizes and addresses will be 0 - or from an old execution)
   */
  if ((stackSize == 0) | (heapSize == 0) | (mmapSize == 0)) {
    printf("Some dynamic segments information was not found yet.\nRun the program with the following switches : -d, -s and -m (Refer to the help for more info).\n");
    return 0;   /* exit program */
  }

  /* Variables holding the info of the segments size */
  long unsigned int textS = (int)&etext - START_DATA,
       dataS = &edata - &etext,
       bssS  = &end - &edata;

  /* Variables holding the info of the address */
  long unsigned int textA = START_DATA,
       dataA = (int)&etext,
       bssA  = (int)&edata;

  // Print file name
  printf("%s :\n", argv[0]);

  printf("section    \t size \t\t addr\n");

  printf("Stack      \t0x%lx  \t0x%lx\n", stackSize, stackAddr);
  printf("Heap       \t0x%lx  \t0x%lx\n", heapSize, heapAddr);
  printf("Memory Map \t0x%lx  \t0x%lx\n", mmapSize, mmapAddr);

  printf(".text      \t0x%lx  \t\t0x%lx\n", textS, textA);
  printf(".data      \t0x%lx  \t0x%lx\n", dataS, dataA);
  printf(".bss       \t0x%lx  \t\t0x%lx\n", bssS, bssA);


  // Unmap the memory
  /* munmap(ptr, filestat.st_size); */

  exit(EXIT_SUCCESS);
  return 0;
}
