
> I'm facing the same issue, here is how I fixed it.
> The cause of the problem could be libssl version, the sdk doesn't support libssl3 yet, so we have to install libssl1.1 manually:
> 
> ``` Bash
> wget http://archive.ubuntu.com/ubuntu/pool/main/o/openssl/libssl1.1_1.1.0g-2ubuntu4_amd64.deb
> sudo dpkg -i libssl1.1_1.1.0g-2ubuntu4_amd64.deb
> ```# speaker_diarization
