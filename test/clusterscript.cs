
cluster_root: /digg

>>
roles:php.*,dbslave.*
runmode:host 
---

echo "hello world" > [[[cluster_root]]]/[[[clusterId]]]/[[[service]]]/file.out

<<

>>
roles:php1-3
runmode:hostwithrole
shell:python
cluster_root:/foo
---


echo "blah blah"

<<
