#include "fdlibm/fdlibm.h"

#include <stdio.h>
// LCOV_EXCL_START
int main(int argc, char *argv[])
{
    for(int i = 1; i < argc; i++) {
        FILE *f = fopen(argv[i], "r");
        double x = 0;
        double y[2] = {0, 0};
        fscanf(f, "%lf %lf %lf", &x, &y[0], &y[1]);
        a(x,y);
    }
    return 0;
}
// LCOV_EXCL_STO