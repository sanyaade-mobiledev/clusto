cluster_root:/digg
mykey:myvalue
>>
name:test task
services:php.*,dbslave.*
runmode:host 
---

echo "hello world" > [[[cluster_root]]]/[[[clusterId]]]/[[[service]]]/file.out

<<


>>
name:test task II
services:php.*
runmode:host
---

echo "hello world" > [[[cluster_root]]]/[[[clusterId]]]/[[[service]]]/file.out

<<
