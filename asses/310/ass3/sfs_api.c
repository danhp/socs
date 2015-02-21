// Simple File System | Comp310 Assignment 4
// Written 2014/12/04
// Daniel Pham
// 260 526 252

#include <stdio.h>
#include <stdlib.h>
#include <time.h>
#include <unistd.h>
#include <string.h>

#include "disk_emu.h"

/* DEFINITIONS */
#define MAX_FILES 300
#define BLOCK_SIZE 1000
#define MAX_BLOCK 10000

#define DIR_ADDRESS 0
#define FREE_LIST_ADDRESS 7
#define FAT_ADDRESS 9000

#define FREE -1
#define USED 0

/* GLOBAL VARIABLES */
const char *FILENAME = "sfs.dsk";

/* HELPER FUNCTIONS */
int read_stream(void *stream, int size, int block);
void write_stream(void *stream, int size, int block);
void write_file(char *stream, int size, int block, int fileID);

/* DATA STRUCTURES */
struct directory_entry{
    char name[16];
    int size;
    int date;
    int FAT_index;
};

struct directory_entry directory[MAX_FILES];

int FAT[MAX_BLOCK][2];

int free_list[MAX_BLOCK];

struct fdt_entry{
    int read_ptr;
    int write_ptr;
    int directory_index;
};

struct fdt_entry FDT[MAX_FILES];

/* API FUNCTIONS */

// Creates the File System
// Initiates data structures.
// returns 0 on success, -1 on failure.
int mksfs(int fresh){

    // Compute data structures sizes
    int dir_size = MAX_FILES * sizeof(struct directory_entry);
    int FAT_size = 2 * MAX_BLOCK * sizeof(int);
    int free_list_size = MAX_BLOCK * sizeof(int);

    int i;
    if (fresh == 0 ){

        // Create a new emulated disk
        if (init_disk((char*)FILENAME, BLOCK_SIZE, MAX_BLOCK) == -1){
            exit(-1);
        }

        // Read data structures to memory
        read_stream(directory, dir_size, DIR_ADDRESS);
        read_stream(free_list, free_list_size, FREE_LIST_ADDRESS);
        read_stream(FAT, FAT_size, FAT_ADDRESS);

    } else {

        // Clear data structures.
        for (i = 0; i < MAX_FILES; i++){
            // Directories
            strcpy(directory[i].name, "");
            directory[i].size = FREE;
            directory[i].date = FREE;
            directory[i].FAT_index = FREE;

            // File descriptor table.
            FDT[i].read_ptr = FREE;
            FDT[i].write_ptr = FREE;
            FDT[i].directory_index = FREE;
        }

        for (i = 0; i < MAX_BLOCK; i++) {
            // clear free list
            free_list[i] = FREE;

            // clear FAT
            FAT[i][0] = FREE;
            FAT[i][1] = FREE;
        }

        // Create a new emulated disk
        if (init_disk((char*)FILENAME, BLOCK_SIZE, MAX_BLOCK) == -1){
            exit(-1);
        }

        // Read data structures to memory
        // Directories go form block 0-6
        // Free list go form block 7-47
        write_stream(directory, dir_size, DIR_ADDRESS);
        write_stream(free_list, free_list_size, FREE_LIST_ADDRESS);
        write_stream(FAT, FAT_size, FAT_ADDRESS);

        // Updtate free list
        for (i = 0; i < 47; i++){
            free_list[i] = USED;
        }

        for (i = FAT_ADDRESS; i < MAX_BLOCK; i++){
            free_list[i] = USED;
        }
    }
    return 0;
}

// List the files in the root directory
void sfs_ls(void){
    int i;
    int isEmpty = 1;

    printf("Listing directory content.\n");

    for (i = 0; i < MAX_FILES; i++){
        if (directory[i].FAT_index != FREE){
            printf("%s\t\t%d\t\t%d\t\t%d\n", directory[i].name, directory[i].size, directory[i].FAT_index, directory[i].date);
            isEmpty = 0;
        }
    }

    if (isEmpty){
        puts("Direcotry is Empty");
    }
}

// Opens a given file
// returns -1 if the file cannot open.
int sfs_fopen(char *name){
    int i, j, free_list_index, FAT_index;

    // Search in current directory
    for (i = 0; i < MAX_FILES; i++){
        if (!strcmp(directory[i].name, name)){
            for (j = 0; j < MAX_FILES; j++){
                if (FDT[j].directory_index == FREE){
                    FDT[j].directory_index = directory[i].FAT_index;
                    FDT[j].read_ptr = 0;
                    FDT[j].write_ptr = directory[i].size;
                    return FDT[j].directory_index;
                }
            }
        }
    }

    // File not found.
    // Allocate blocks.

    // Find free block
    for (free_list_index = 0; free_list_index < MAX_BLOCK && free_list[free_list_index] == USED; free_list_index++){
        // Only index matters.
    }
    if (free_list_index >= MAX_BLOCK){
        // No empty block
        return -1;
    }

    // Set block
    free_list[free_list_index] = USED;

    // Find free FAT entry
    for (FAT_index = 0; FAT_index < MAX_BLOCK && FAT[FAT_index][0] != FREE; FAT_index++){
        // Only index matters.
    }
    if (FAT_index >= MAX_BLOCK){
        // No empty block
        return -1;
    }

    // entry points to allocated block
    FAT[FAT_index][0] = free_list_index;
    FAT[FAT_index][1] = EOF;

    // Find free directory entry
    for (i = 0; i < MAX_FILES && directory[i].size != -1; i++){
        // Only index matters.
    }
    if (i >= MAX_FILES){
        return -1;
    }

    // Initialize file
    strcpy(directory[i].name, name);
    directory[i].size = 0;
    directory[i].date = (int)time(NULL);
    directory[i].FAT_index = FAT_index;

    // Find free entry in FDT
    for (i = 0; i < MAX_FILES && FDT[i].directory_index != FREE; i++){
        // Only index matters.
    }
    if (i >= MAX_FILES){
        return -1;
    }

    // Set FDT Entry
    FDT[i].directory_index = FAT_index;
    FDT[i].read_ptr = 0;
    FDT[i].write_ptr = 0;

    return FDT[i].directory_index;
}

// Closes a given file
int sfs_fclose(int fileId){
    int i;

    for (i = 0; i < MAX_FILES; i++){
        if (FDT[i].directory_index == fileId){
            FDT[i].directory_index = FREE;
            FDT[i].read_ptr = 0;
            FDT[i].write_ptr = 0;

            // Success
            return 0;
        }
    }

    // Not found
    puts("File not found.");
    return -1;

}

// Write buffer characters to disk.
int sfs_fwrite(int fileId, char *buffer, int length){
    int i, block;

    for (i = 0; i < MAX_FILES && FDT[i].directory_index != fileId; i++){
        // Only index matters.
    }

    directory[fileId].size += length;

    block = (FDT[i].write_ptr) / BLOCK_SIZE;

    // write to disk.
    write_file(buffer, strlen(buffer), block, fileId);

    return 0;
}

// Read characters from disk to buffer.
int sfs_fread(int fileId, char *buffer, int length){
    int i, block, remainder;
    int bytes_read = 0;

    if (fileId == -1){
        return -1;
    }

    char tmp_buffer[BLOCK_SIZE] = "";

    for (i = 0; i < MAX_FILES && FDT[i].directory_index != fileId; i++){
        // Only index matters.
    }
    if (i >= MAX_FILES){
        return -1;
    }

    block = (FDT[i].read_ptr + 1) / BLOCK_SIZE;
    remainder = abs(BLOCK_SIZE - FDT[i].read_ptr);

    bytes_read += read_blocks(block, 1, tmp_buffer);

    if (length <= remainder){
        memcpy(buffer, tmp_buffer + (FDT[i].read_ptr % BLOCK_SIZE), length);
        FDT[i].read_ptr +=  length;
        length = 0;
    } else {
        memcpy(buffer, tmp_buffer + (FDT[i].read_ptr % BLOCK_SIZE), remainder);
        FDT[i].read_ptr += length;
        length -= remainder;
    }

    block = FAT[FDT[i].directory_index][1];

    while (block != EOF && length > 0){
        bytes_read += read_blocks(block, 1, tmp_buffer);

        if (length > BLOCK_SIZE){
            memcpy(buffer + bytes_read, tmp_buffer, BLOCK_SIZE);
            length -= BLOCK_SIZE;
            FDT[i].read_ptr += BLOCK_SIZE;
        } else {
            memcpy(buffer + bytes_read, tmp_buffer, length);
            length = 0;
            FDT[i].read_ptr += length;
        }

        block = FAT[FDT[i].directory_index][1];
    }

    return bytes_read;
}

// Seek to location from beginning.
// Modify read and write pointer.
int sfs_fseek(int fileId, int offset){
    int i;

    for (i = 0; i < MAX_FILES; i++){
        if (FDT[i].directory_index == fileId){
            FDT[i].read_ptr = offset;
            FDT[i].write_ptr = offset;

            return 0;
        }
    }

    // File not found.
    puts("File not found");
    return -1;
}

// Removes a file from the FileSystem.
int sfs_remove(char *file){
    int i, block;

    // Find file index
    for (i = 0; i < MAX_FILES && strcmp(directory[i].name, file); i++){
        // Only index matters.
    }
    if (i >= MAX_FILES){
        puts("File not found");
        return -1;
    }

    int tmp_index = directory[i].FAT_index;

    // Clear directory entry
    strcpy(directory[i].name, "");
    directory[i].size = FREE;
    directory[i].date = FREE;
    directory[i].FAT_index = FREE;

    while (tmp_index != EOF){
        block = FAT[tmp_index][0];
        free_list[block] = FREE;
        FAT[tmp_index][0] = FREE;
        FAT[tmp_index][1] = EOF;

        tmp_index = FAT[tmp_index][1];
    }

    return 0;
}

/* HELPER FUNCTIONS */
int read_stream(void *stream, int size, int block){
    int pos = 0;
    int bytes_read = 0;
    char buffer[BLOCK_SIZE];

    while (size > 0){
        bytes_read += read_blocks(block, 1, buffer);

        if (size > BLOCK_SIZE){
            memcpy(stream + pos, buffer, BLOCK_SIZE);
        } else {
            memcpy(stream + pos, buffer, size);
        }

        size -= BLOCK_SIZE;
        pos =+ BLOCK_SIZE;
        block++;
    }

    return bytes_read;
}

void write_stream(void *stream, int size, int block){
    char buffer[BLOCK_SIZE];
    int pos = 0;

    for ( ; size > 0; block++){
        if (size > BLOCK_SIZE){
            memcpy(buffer, stream + pos, BLOCK_SIZE);
        } else {
            memcpy(buffer, stream + pos, size);
        }

        write_blocks(block, 1, buffer);

        size -= BLOCK_SIZE;
        pos += BLOCK_SIZE;
    }
}

void write_file(char *stream, int size, int block, int fileId){
    int free_list_index, FAT_index;
    int i, j, pos = 0;

    for (i = 0; i < MAX_FILES && FDT[i].directory_index != fileId; i++){
        // Only index matters
    }

    for (j = 0; j < MAX_FILES && directory[j].FAT_index != fileId; j++){
        // Only index matters.
    }

    int remainder = BLOCK_SIZE - (FDT[i].write_ptr % BLOCK_SIZE);

    char buffer[BLOCK_SIZE] = "";
    read_blocks(block, 1, buffer);

    if (size <= remainder){
        memcpy(buffer + (FDT[i].write_ptr % BLOCK_SIZE), stream, size);

        FDT[i].write_ptr += size;
        directory[i].date = time(0);
        size = 0;
    } else {
        memcpy(buffer + (FDT[i].write_ptr % BLOCK_SIZE), stream, remainder);

        FDT[i].write_ptr += remainder;
        directory[i].date = time(0);
        pos = remainder;
    }

    write_blocks(block, 1, buffer);

    while (size > 0){
        for (free_list_index = 0; free_list_index < MAX_BLOCK && free_list[free_list_index] != FREE; free_list_index++){
            // only index matters.
        }

        free_list[free_list_index] = USED;

        for (FAT_index = 0; FAT_index < MAX_BLOCK && FAT[FAT_index][0] != FREE; FAT_index++){
            // Only index matters.
        }

        FAT[block][1] = FAT_index;
        FAT[FAT_index][0] = free_list_index;
        FAT[FAT_index][1] = EOF;
        block = free_list_index;

        if (size <= BLOCK_SIZE){
            memcpy(buffer, stream + pos, size);
            FDT[i].write_ptr += size;
        } else {
            memcpy(buffer, stream + pos, BLOCK_SIZE);
            FDT[i].write_ptr += BLOCK_SIZE;
        }

        write_blocks(block, 1, buffer);

        size -= BLOCK_SIZE;
        pos += BLOCK_SIZE;

        directory[j].date = time(0);
    }
}
