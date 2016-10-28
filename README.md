# Hevi - Froeling Lambdatronic Client

Load data from Froeling firewood boilers that are using Lambdatronic S3200 and submit it to [froeling.io](https://froeling.io). 

## Useage

```
usage: hevi   [-h] --config CONFIG [-v] [--version]
              [--submit | --test | --values | --schema | --state | --errors | --menu | --date]

optional arguments:
  -h, --help       show this help message and exit
  --config CONFIG  Path to the configuration file
  -v, --verbose    Enable verbose logging
  --version        Show hevi version
  --submit         Load data and submit it to froeling.io
  --test           Test connection to heating
  --values         Load and display all recent values
  --schema         Load recent values schema
  --state          Lost state
  --errors         Load errors
  --menu           Load menu structure
  --date           Load device date and version
```

## Logging/Debug

Log files can be found in `~/.hevi/hevi.log`.

## Compatible devices

For now, I have only access to an S4 Turbo. Feel free to contact me, if you want to help me expanding the range of compatible devices.

### Tested
 - Froeling S4 Turbo

### Maybe Compatible - Untested
 - Froeling S4 Turbo F
 - Froeling P4

Basically, every Froeling boiler using a Lambdatronic S3200 might be compatible.   

### Lambdatronic S3100

I don't know if S3100 is using the same protocol like the S3200 or if it even offers an accessible interface.

## Todo

- [ ] Add unit tests
- [ ] Create deb/aur packages 

## Contributing 

Pull requests and bug reports are very welcome :)
If you're reporting a bug, please also provide logs, the device type and as much detailed description as possible.  

## Links

- [froeling.io](https://froeling.io)
- Offical froeling website: [http://www.froeling.com](http://www.froeling.com/)

## License 

```
Copyright 2016 Sebastian Chlan

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License.
You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.
```
