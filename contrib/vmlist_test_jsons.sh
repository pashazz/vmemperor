#!/bin/sh
cat - |  grep DEBUG | grep VmEmperorAfterLoginTest: | awk '{split($0, a, "VmEmperorAfterLoginTest:");  match(a[2], /({.*})/, arr); print(arr[0]);}'
