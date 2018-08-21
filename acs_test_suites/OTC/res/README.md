### Resource Registry
File path: `acs_test_suites/OTC/res/resources.csv`

Field description:

* *Domain*: domain like Audio/Graphics etc.
* *Relative Path*: the relative path used in your code
* *Type*: file type, available choices: `apk, audio, video, script, others`
* *Original Source*: the original source, NOT internal link, should able to be visit from outside network.
* *License*: license of the resource file
* *Convert Commands*: if you need some process to the original source, you can use this field. If this field not set, _Original Source_ will directly copy to _Relative Path_.


#### Convert Commands
_Convert Commands_ is used when you need to have some process with _Original Source_ file.
> for example: the original source is a .wav file, and you want to convert into .mp3, you can specified convert command here.

There are 2 environment variables available:

* `src`: you can use `$src` to represent “Original Source” in the table, we will help you to download the file first.
* `dst`: `$dst` to represent “Relative Path” in the table

Example:

* Relative Path: `resources/Audio/test_sample.mp3`
* Original Source: `https://example.com/files/wav_sample.wav`
* Convert Commands: `ffmpeg -y -i $src -vn -ar 44100 -ac 2 -ab 192k -f mp3 $dst`

##### Script Support
Script is also supported if you need complex operation on original resources, you can put your script under `scripts/` folder.

For example, we need to extract an .apk file from Google CTS package, a script `scripts/zip_extract.py` is added to extract file from zip compression,
and you can use it as below:

* Relative Path: `resources/Demo/CtsSimpleApp.apk`
* Original Source: `https://dl.google.com/dl/android/cts/android-cts-8.1_r7-linux_x86-x86.zip`
* Convert Commands: `scripts/zip_extract.py $src android-cts/testcases/CtsSimpleApp.apk $dst`


### Download Resources
use `acs_test_suites/OTC/res/download.py` to download sources, it will put all resource under `~/.acs-resources/` folder

If you just want to download specified domain resources, you can use `-d DOMAIN` options, for example: `python download.py -d Audio`
