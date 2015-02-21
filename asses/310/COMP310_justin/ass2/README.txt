JUSTIN DOMINGUE - 260588454

COMP 310
--------

## Assignment 2 - Memory Layout Printer

### Segment Sizes Found By My Program

        SECTION           SIZE         ADDR
        Stack          0x7feb2   0xbfa211b0
        Heap        0x4c5df400    0x815a008
        Memory Map  0x2f69ec8c   0xb7724000
        .text            0xe66    0x8048000
        .data           0x21de    0x8048e66
        .bss              0x20    0x804b044

**Note.** All sizes are in bytes. I tried to reproduce the layout of the output of the `size` command.

### How To

Since `alloca`'s return value is implementation-dependent, I had to let the program crash (Segmentation Fault) once it can't allocate any more stack memory.

A similar behavior was found for the __memory map__.

For that reason, I decided to use switches to invoke different parts of the program.

#### Switches

- `-d` : Heap (dynamic) segment size
- `-s` : Stack segment size
- `-m` : Memory Map segment size
- `-h` : Show the help

Running the executable with a switch will run a particular portion of the code. For example, `-d` will find the heap segment size and exit after finding it. The program uses a log file (`size_log`) to log the values found a each execution.

**Note.** Calling the program _without_ a switch will show the information on the file (loading the sizes and addresses from the log file).
