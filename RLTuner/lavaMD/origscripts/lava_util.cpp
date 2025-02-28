
#define NUMBER_PAR_PER_BOX 100							
typedef struct nei_str
{
    int x, y, z;
    int number;
    long offset;

} nei_str;


typedef struct box_str
{
    int x, y, z;
    int number;
    long offset;
    int nn;
    nei_str nei[26];
} box_str;

void initAll(box_str* box_cpu, int boxes1d_arg){
    int i, j, k, l,m,n;
    int nh;
    for(i=0; i<boxes1d_arg; i++){
        for(j=0; j<boxes1d_arg; j++){
            for(k=0; k<boxes1d_arg; k++){
                box_cpu[nh].x = k;
                box_cpu[nh].y = j;
                box_cpu[nh].z = i;
                box_cpu[nh].number = nh;
                box_cpu[nh].offset = nh * NUMBER_PAR_PER_BOX;
                box_cpu[nh].nn = 0;
                for(l=-1; l<2; l++){
                    for(m=-1; m<2; m++){
                        for(n=-1; n<2; n++){
                            if(		(((i+l)>=0 && (j+m)>=0 && (k+n)>=0)==true && ((i+l)<boxes1d_arg && (j+m)<boxes1d_arg && (k+n)<boxes1d_arg)==true)	&&
                                    (l==0 && m==0 && n==0)==false	){

                                // current neighbor box
                                box_cpu[nh].nei[box_cpu[nh].nn].x = (k+n);
                                box_cpu[nh].nei[box_cpu[nh].nn].y = (j+m);
                                box_cpu[nh].nei[box_cpu[nh].nn].z = (i+l);
                                box_cpu[nh].nei[box_cpu[nh].nn].number = (box_cpu[nh].nei[box_cpu[nh].nn].z * boxes1d_arg * boxes1d_arg) + 
                                    (box_cpu[nh].nei[box_cpu[nh].nn].y * boxes1d_arg) + 
                                    box_cpu[nh].nei[box_cpu[nh].nn].x;
                                box_cpu[nh].nei[box_cpu[nh].nn].offset = box_cpu[nh].nei[box_cpu[nh].nn].number * NUMBER_PAR_PER_BOX;
                                box_cpu[nh].nn = box_cpu[nh].nn + 1;
                            }
                        } 
                    }
                }
                nh = nh + 1;
            } 
        } 
    }
}
