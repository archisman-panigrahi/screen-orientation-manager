---
name: Device autodetect support
about: If you want device support for autodetect, use this
title: ''
labels: ''
assignees: ''

---

Please add the output of `xinput list` while running XOrg/X11 (Wayland will not work)



Please add the output of `cat /sys/firmware/devicetree/base/model` (note that it may not exist in some devices, that is fine)




Please add the output of `cat /sys/devices/virtual/dmi/id/product_name` (note that it may not exist in some devices, that is fine)
