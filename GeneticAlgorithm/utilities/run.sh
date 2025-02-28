#!/bin/bash

QUALITY=${APPROX_UTIL_ROOT}/quality.py

algorithm=$2
executable=$3
parameters=$4
threshHold=$5
metric=$6
analysisDir=$1_${threshHold}
LOG="${APPROX_ROOT}/logs/${executable}/"
mkdir -p  ${LOG}

logFile="${LOG}floatsmith_${algorithm}_${threshHold}.log"
errFile="${LOG}floatsmith_${algorithm}_${threshHold}.err"
statsFile="floatsmith_${algorithm}_${threshHold}.stats.txt"
rootDir=$(pwd)

cmd="$executable ${parameters}"
echo "Executable is ${executable} rootDir is ${rootDir} cmd is ${cmd}">${logFile} 2>${errFile}
export THRESHHOLD=$threshHold


rm -rf "$analysisDir"
make clean


start=$(date +%s)
${FLOATSMITH} --ga-num_generation 5 -j 16 -t 10 -g typechain:cluster -M --root $analysisDir  --quality ${QUALITY} --metric ${metric} -B --run "./${cmd} output"  -s $algorithm  >>${logFile} 2>>${errFile}
end=$(date +%s)

runtime=$((end-start))
configurations=$(grep "Testing" ${logFile}  | wc -l)
space=$(grep -w "action" $analysisDir/typeforge_vars.json  | wc -l)
final=$(grep "If found, the recommended configuration is located in" $logFile | cut -d ':' -f 2)

echo "THE RESULT IS">>${logFile} 2>>${errFile}
echo $final>>${logFile} 2>>${errFile}
echo "END">>${logFile} 2>>${errFile}

if [ -d "$final" ]
then
    pushd $final
    make
    cp "$executable" "$rootDir">>${logFile} 2>>${errFile}
    echo "cp $executable $rootDir">>${logFile} 2>>${errFile}
    popd
else
    echo "No configuration was found">>${logFile} 2>>${errFile}
fi 

unset THRESHHOLD
echo "SLEEP">>${logFile} 2>>${errFile}
sleep 1
echo "FINISH">>${logFile} 2>>${errFile}
echo "analysis Time:${runtime}" > ${statsFile}
echo "Configurations:${configurations}">> ${statsFile}
echo "Space:${space}" >> ${statsFile}

