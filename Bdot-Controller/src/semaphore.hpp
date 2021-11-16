#pragma once


#include <stdio.h>
#include <semaphore.h>
#include <unistd.h>
#include <sys/stat.h>
#include <fcntl.h>


#include <iostream>

#define DEFAULT_LOCK_NAME "/fs-semaphore"

using namespace std;

namespace Locks {

    class SemaphoreLock 
    {
        private:
            sem_t *semaphore;
            int semval;
        public:
            SemaphoreLock(const char* sysWideName)
            {
                this->semaphore = sem_open(sysWideName, O_CREAT , 0777, 1);
                if (this->semaphore == SEM_FAILED) 
                {
                    perror("Failed to open System-Wide Semaphore");
                    exit(-1);
                }
            };

            bool check_lock()
            {
                // checks value of the lock and returns a bool
                sem_getvalue(this->semaphore, &this->semval);
                if (this->semval  == 0) return true;
                return false;
            };

            void aquire_lock()
            {
                // implements python semaphore api
                if (sem_wait(this->semaphore) == -1)
                {
                    perror("sem_wait error in aquire_lock");
                    exit(-1);
                }
            };

            void release_lock()
            {
                // implements python's semaphore api
                sem_post(this->semaphore);
            };
    };


};