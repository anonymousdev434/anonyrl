// #include <stdio.h>
// #include <unistd.h>
// #include <stdlib.h>
// #include <string.h>
#include <math.h>
// #include <assert.h>
// #include <stddef.h>

#define RANDOM_MAX 2147483647

#ifndef FLT_MAX
#define FLT_MAX 3.40282347e+38
#endif

#ifdef __SENSITIVITY__
int *stability;
#endif

void writeData(double* ptr, size_t size, int type, char *name);
void writeData(float* ptr, size_t size, int type, char *name);
void writeData(int* ptr, size_t size, int type, char *name);

void readData(FILE *fd, int **ptr,    size_t* numElements);
void readData(FILE *fd, float **ptr,  size_t* numElements);
void readData(FILE *fd, double **ptr, size_t* numElements);
void readValue( FILE *fd, int *val );
void readValue( FILE *fd, long *val);
void MP_memcpy(float *dst, double *src, size_t elements);
void MP_memcpy(double *dst, float *src, size_t elements);
void MP_memcpy(float *dst, float *src, size_t elements);
void MP_memcpy(double *dst, double *src, size_t elements);
void MP_Malloc2D(int sizeY, int sizeX, double ***mt);
void MP_Malloc3D(int sizeZ, int sizeY, int sizeX, double ****mt);
void MP_Malloc2D(int sizeY, int sizeX, float ***mt);
void MP_Malloc3D(int sizeZ, int sizeY, int sizeX, float ****mt);
void MP_Malloc2D(size_t sizeY, size_t sizeX, double ***mt);
void MP_Malloc3D(size_t sizeZ, size_t sizeY, size_t sizeX, double ****mt);
void MP_Malloc2D(size_t sizeY, size_t sizeX, float ***mt);
void MP_Malloc3D(size_t sizeZ, size_t sizeY, size_t sizeX, float ****mt);


void stopMeasure();
void startMeasure();

void omp_set_num_threads(int value){
    return;
}

int omp_get_thread_num(){
    return 0;
}

#define DOUBLE 0
#define FLOAT 1
#define INT 2
#define LONG 3

extern double wtime(void);

int num_omp_threads = 1;
extern double wtime(void);


double euclid_dist_2(double *pt1,
        double *pt2,
        int    numdims)
{
    int i;
    double ans=0.0;
    for (i=0; i<numdims; i++)
        ans += (pt1[i]-pt2[i]) * (pt1[i]-pt2[i]);

    return(ans);
}


int find_nearest_point(double  *pt,          /* [nfeatures] */
        int     nfeatures,
        double **pts,         /* [npts][nfeatures] */
        int     npts)
{
    int index, i;
    double min_dist=FLT_MAX;

    /* find the cluster center id with min distance to pt */
    for (i=0; i<npts; i++) {
        double dist;
        dist = euclid_dist_2(pt, pts[i], nfeatures);  /* no need square root */
        if (dist < min_dist) {
            min_dist = dist;
            index    = i;
        }
    }
    return(index);
}

/*----< kmeans_clustering() >---------------------------------------------*/

double** kmeans_clustering(double **feature,    /* in: [npoints][nfeatures] */
        int     nfeatures,
        int     npoints,
        int     nclusters,
        double   threshold,
        int    *membership,
        int  *iterations) /* out: [npoints] */
{

    int      i, j, k, n=0, index, loop=0;
    int     *new_centers_len;			/* [nclusters]: no. of points in each cluster */
    double  **new_centers;				/* [nclusters][nfeatures] */
    double  **clusters;					/* out: [nclusters][nfeatures] */
    double    delta;

    double   timing;

    int      nthreads;
    int    **partial_new_centers_len;
    double ***partial_new_centers;

    nthreads = num_omp_threads; 
#ifdef __SENSITIVITY__
    stability = (int*) malloc (sizeof(int)*npoints);
    for ( i = 0; i <npoints; i++)
        stability[i] = 0;
#endif
    /* allocate space for returning variable clusters[] */
    MP_Malloc2D(nclusters,nfeatures,&clusters);

    /* randomly pick cluster centers */
    for (i=0; i<nclusters; i++) {
        //n = (int)rand() % npoints;
        for (j=0; j<nfeatures; j++)
            clusters[i][j] = feature[n][j];
        n++;
    }

    for (i=0; i<npoints; i++)
        membership[i] = -1;

    /* need to initialize new_centers_len and new_centers[0] to all 0 */
    new_centers_len = (int*) calloc(nclusters, sizeof(int));

    MP_Malloc2D(nclusters, nfeatures, &new_centers);


    partial_new_centers_len    = (int**) malloc(nthreads * sizeof(int*));
    partial_new_centers_len[0] = (int*)  calloc(nthreads*nclusters, sizeof(int));
    for (i=1; i<nthreads; i++)
        partial_new_centers_len[i] = partial_new_centers_len[i-1]+nclusters;

    MP_Malloc3D(nthreads, nclusters, nfeatures, &partial_new_centers);

    printf("num of threads = %d\n", num_omp_threads);
    do {
        delta = 0.0;
        omp_set_num_threads(num_omp_threads);
#pragma omp parallel \
        shared(feature,clusters,membership,partial_new_centers,partial_new_centers_len)
        {
            int tid = omp_get_thread_num();				
#pragma omp for \
            private(i,j,index) \
            firstprivate(npoints,nclusters,nfeatures) \
            schedule(static) \
            reduction(+:delta)
            for (i=0; i<npoints; i++) {
                /* find the index of nestest cluster centers */					
                index = find_nearest_point(feature[i], nfeatures, clusters, nclusters);				

                /* if membership changes, increase delta by 1 */
                if (membership[i] != index) delta += 1.0;

                /* assign the membership to object i */
                membership[i] = index;

                /* update new cluster centers : sum of all objects located
                   within */
                partial_new_centers_len[tid][index]++;				
                for (j=0; j<nfeatures; j++)
                    partial_new_centers[tid][index][j] += feature[i][j];
            }
        } /* end of #pragma omp parallel */

        /* let the main thread perform the array reduction */
        for (i=0; i<nclusters; i++) {
            for (j=0; j<nthreads; j++) {
                new_centers_len[i] += partial_new_centers_len[j][i];
                partial_new_centers_len[j][i] = 0.0;
                for (k=0; k<nfeatures; k++) {
                    new_centers[i][k] += partial_new_centers[j][i][k];
                    partial_new_centers[j][i][k] = 0.0;
                }
            }
        }    

        /* replace old cluster centers with new_centers */
        for (i=0; i<nclusters; i++) {
            for (j=0; j<nfeatures; j++) {
                if (new_centers_len[i] > 0)
                    clusters[i][j] = new_centers[i][j] / new_centers_len[i];
                new_centers[i][j] = 0.0;   /* set back to 0 */
            }
            new_centers_len[i] = 0;   /* set back to 0 */
        }

    } while (loop++ < *iterations);
    *iterations = loop;

    free(new_centers[0]);
    free(new_centers);
    free(new_centers_len);
#ifdef __SENSITIVITY__
    free(stability);
#endif

    return clusters;
}

int *cluster(int      numObjects,      /* number of input objects */
        int      numAttributes,   /* size of attribute of each object */
        double** attributes,      /* [numObjects][numAttributes] */            
        int      nclusters,
        double threshold,       /* in:   */
        double ***cluster_centres, /* out: [best_nclusters][numAttributes] */
        int *iterations 
        )
{
    int    *membership;
    double **tmp_cluster_centres;

    membership = (int*) malloc(numObjects * sizeof(int));

    srand(7);
    /* perform regular Kmeans */
    tmp_cluster_centres = kmeans_clustering(attributes,
            numAttributes,
            numObjects,
            nclusters,
            threshold,
            membership,
            iterations);      

    if (*cluster_centres) {
        free((*cluster_centres)[0]);
        free(*cluster_centres);
    }
    *cluster_centres = tmp_cluster_centres;

    return membership;
}


/*---< usage() >------------------------------------------------------------*/
void usage(char *argv0) {
    const char *help =
        "Usage: %s [switches] -i filename\n"
        "       -i filename     		: file containing data to be clustered\n"
        "       -k                 	: number of clusters (default is 5) \n"
        "       -l                 	: number of iterations(default is 5) \n"
        "       -t threshold		: threshold value\n"
        "       -n no. of threads	: number of threads\n";
    "       -o filename     	: Output filename\n";
    fprintf(stderr, help, argv0);
    exit(-1);
}

/*---< main() >-------------------------------------------------------------*/
int main(int argc, char **argv) {
    int     opt;
    extern char   *optarg;
    extern int     optind;
    int     nclusters=5;
    char   *filename = 0;           
    double  *buf;
    double **attributes;
    double **cluster_centres=NULL;
    int     i, j;

    int     numAttributes;
    int     numObjects;        
    char    line[1024];           
    int     isBinaryFile = 0;
    int     nloops = 1;
    double   threshold = 0.001;
    double  timing;		   
    int iterations = 80;
    char *memberShipName = NULL;

    while ( (opt=getopt(argc,argv,"i:k:t:n:l:o:?"))!= EOF) {
        switch (opt) {
            case 'i': filename=optarg;
                      break;
            case 't': threshold=atof(optarg);
                      break;
            case 'k': nclusters = atoi(optarg);
                      break;			
            case 'n': num_omp_threads = atoi(optarg);
                      break;
            case 'l': iterations= atoi(optarg);
                      printf("Iterations are %d\n",iterations);
                      break;
            case 'o': memberShipName =  optarg;
                      break;
            case '?': usage(argv[0]);
                      break;
            default: usage(argv[0]);
                     break;
        }
    }


    if (filename == 0) usage(argv[0]);

    numAttributes = numObjects = 0;

    /* from the input file, get the numAttributes and numObjects ------------*/

    FILE *infile;
    if ((infile= fopen(filename, "rb")) == NULL) {
        fprintf(stderr, "Error: no such file (%s)\n", filename);
        exit(1);
    }
    readValue(infile, &numObjects);
    readValue(infile, &numAttributes);
    size_t numElements = 0;
    readData(infile, &buf, &numElements);
    if ( numElements != numObjects*numAttributes){
        printf("Input file is not valid %ld %d %d\n",numElements, numObjects,numAttributes);
        exit(0);
    }

    MP_Malloc2D( numObjects, numAttributes,&attributes);

    fclose(infile);

    printf("I/O completed\n");	

    MP_memcpy(attributes[0], buf, numObjects*numAttributes);

    int *membership;
    startMeasure();
    printf("Iterations are %d\n", iterations);
    for (i=0; i<nloops; i++) {
        cluster_centres = NULL;
        membership = cluster(numObjects,
                numAttributes,
                attributes,           /* [numObjects][numAttributes] */                
                nclusters,
                threshold,
                &cluster_centres, 
                &iterations
                );
    }
    stopMeasure();
    printf("Iterations performed:%d\n",iterations);

    if ( memberShipName != NULL ){
        printf("I am creating output\n");
        size_t tmpSize = numObjects;
        writeData(membership, tmpSize, INT, memberShipName);
    }
    free(membership);
    free(attributes);
    free(cluster_centres[0]);
    free(cluster_centres);
    free(buf);
    return(0);
}

