#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <math.h>

const char *supportedMetrics[] = {
    "MSE",
    "MAE",
    "RMSE",
    "R2",
    "MPP" //miss position percentage
};

int numMetrics = 5;
double epsilon = -1;


void printSupportedMetrics(){
    int i;
    for ( i = 0 ; i < numMetrics ; i++)
        printf("%s\n", supportedMetrics[i]);
}
const char *show_classification(double x) {
    switch(fpclassify(x)) {
        case FP_INFINITE:  return "Inf";
        case FP_NAN:       return "NaN";
        case FP_NORMAL:    return "normal";
        case FP_SUBNORMAL: return "subnormal";
        case FP_ZERO:      return "zero";
        default:           return "unknown";
    }
}
int isNumber(double *test, size_t elements){
    size_t i;
    for ( i = 0; i < elements; i++){
        if ( fpclassify(test[i]) != FP_ZERO && fpclassify(test[i]) != FP_NORMAL){ 
            return 0;
        }
    }
    return 1;
}

double computeMAE(double *correct, double *test, size_t elements){
    double error =0.0;
    size_t i;
    double diff = 0.0;
    for ( i = 0 ; i < elements; i++){
        if ( *(long*) &correct[i] != *(long*) &test[i]){
            diff = fabs(correct[i] - test[i]);
            error += diff;
        }
    }
    error = error/ (double) elements;
    // store log.txt as error record
    bool verified;
    if (error <= epsilon) {
      verified = true;
    }
    else {
        verified = false;
    }
    FILE *fp = fopen("./log.txt", "w");
    fputs(verified ? "true\n" : "false\n", fp);
    fprintf(fp, "%20.13E\n", error);

    return error;
}

double computeMSE(double *correct, double *test, size_t elements){
    double error =0.0;
    double sqrtDiff= 0;0;
    double p2Diff = 0.0;
    size_t i;
    for ( i = 0 ; i < elements; i++){
        double tmp = correct[i] - test[i];
        p2Diff = pow(tmp,2.0);
        error += p2Diff;
    }
    error = error/(double)elements;
    return error;
}

double computeRMSE(double *correct, double *test, size_t elements){
    double error = computeMSE(correct,test,elements);
    error = sqrt(error);
    return error;
}

double computeRootSquared(double *correct, double *test, size_t elements){
    size_t i; 
    double avgValue = 0.0;
    double SSReg = 0.0;
    double SSTot = 0.0;

    for ( i = 0 ; i < elements; i++)
        avgValue += correct[i];
    avgValue = avgValue / (double) elements;

    for ( i = 0; i < elements; i++){
        double diff = test[i]-avgValue;
        SSReg += pow(diff,2); 
        diff = correct[i]-avgValue;
        SSTot += pow(diff,2);
    }
    return SSReg/SSTot;
}

double computeQuality(double *correct, double *test, size_t elements, char *metric, int eps){

    switch (eps)
    {
    case 3:
        epsilon = 1e-3;
        break;
    case 4:
        epsilon = 1e-4;
        break;
    case 6:
        epsilon = 1e-6;
        break;
    case 8:
        epsilon = 1e-8;
        break;
    case 10:
        epsilon = 1e-10;
        break;
    default:
        break;
    }

    if  ( !isNumber(test, elements) ) {
        // store log.txt as error record
        bool verified;
        verified = false;

        FILE *fp = fopen("./log.txt", "w");
        fputs(verified ? "true\n" : "false\n", fp);
        fprintf(fp, "NaN\n");
        return 1.0;
    }

    if ( strcmp(metric,"MAE") == 0 )
        return computeMAE(correct, test, elements);
    else if (strcmp( metric, "RMSE") == 0 )
        return computeRMSE(correct, test, elements);
    else if (strcmp( metric, "MSE") == 0 )
        return computeMSE(correct, test, elements);
    else if (strcmp( metric, "R2") == 0 )
        computeRootSquared(correct, test, elements);
    else{
        printf("Please specify a valid quality metric\n");
    }
}

double computeMPP(int *correct, int *test, size_t elements){
    size_t i;
    double wrong = 0.0;
    int flag = 0;
    double error =0.0;
    for ( i = 0 ; i < elements; i++){
        if ( correct[i] != test[i] ){
            wrong+=1.0;
            flag = 1;
        }
    }
    
    if (flag)
      error = wrong/(double) elements;
    else
      error = 0.0;
    // store log.txt as error record
    bool verified;
    if (error <= epsilon) {
      verified = true;
    }
    else {
        verified = false;
    }
    FILE *fp = fopen("./log.txt", "w");
    fputs(verified ? "true\n" : "false\n", fp);
    fprintf(fp, "%20.13E\n", error);

    if (flag)
      return wrong/(double) elements;
    else
      return 0.0;
}

double computeQuality(int *correct, int* test, size_t elements, char *metric, int eps){

    switch (eps)
    {
    case 3:
        epsilon = 1e-3;
        break;
    case 4:
        epsilon = 1e-4;
        break;
    case 6:
        epsilon = 1e-6;
        break;
    case 8:
        epsilon = 1e-8;
        break;
    case 10:
        epsilon = 1e-10;
        break;
    default:
        break;
    }

    if ( strcmp(metric,"MPP") == 0 ){
        return computeMPP(correct, test, elements);
    }
    else{
        printf("Please specify a valid quality metric\n");
    }
}

int checkMetrics(const char *metric){
    int i;
    for ( i = 0 ; i < numMetrics; i++){
        if (strcmp(metric,supportedMetrics[i])==0)
            return 1;
    }
    return 0;
}
