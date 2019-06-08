#!/bin/bash

curl -L -o counts.txt https://drive.google.com/uc?id=1e5IY1FTw3qAJ7SiIhwdR3RG0tYX_v7eZ
curl -L -o vocabulary.txt https://drive.google.com/uc?id=1jr7WDwgi0IZDidiRsXuqfDnk17dQXx4X
curl -L -o val_df.csv https://drive.google.com/uc?id=1q-RqMEhWHQS28nT_Ajf8CfuWJsFdzJwk
curl -L -o error_df.csv https://drive.google.com/uc?id=1zhut8Cn_IO3sRtUHYXaqeewUdnZ6gYQx
curl -L -o normal_vocabulary.txt https://drive.google.com/uc?id=1WpZdcsw1cU1OcrLgxw2VdoQG80IMx9X0
curl -L -o val_df_lm.csv https://drive.google.com/uc?id=1iBOqWJvGCNBkgU8JhBZBPmoVSoKlDobv
curl -L -o old_rus_lm.pth https://drive.google.com/uc?id=1AYXmzBuTkQBILAj0OpaOLGrBsaRHbmS_

echo "Download done!"
