# Guide to Downloading the SGDP Dataset

This README provides step-by-step instructions for downloading the SGDP dataset using GridFTP from Fermi Lab.

## Prerequisites

### 1. Obtain a Personal Grid x509 Certificate
You must obtain a personal certificate to download data [cite: 2].
- **Option A:** Follow the instructions at [Fermi Service-Now KB0010815](https://fermi.service-now.com/kb_view.do?sysparm_article=KB0010815) [cite: 3, 4].
  - Use the Virtual Organization (**VO**): **SCDA** [cite: 5].
- **Option B:** If you are from an institute included in CILogon (other than Google), use [cilogon.org](https://cilogon.org) [cite: 6, 7].

### 2. Certificate Installation and Registration
1. Once you receive your certificate, follow the email instructions to upload it to your browser [cite: 8].
2. **Action Required:** Send the certificate subject (which will look like `/DC=org/DC=cilogon/C=US/O=Google/CN=User Name A16321`) to `ifisk@simonsfoundation.org` [cite: 8].
3. If using Globus tools on Linux/UNIX, follow [these instructions](https://fermi.service-now.com/kb_view.do?sysparm_article=KB0010815) immediately using the **same browser window** [cite: 9, 10].
   - *Note: Do not wait too long, or the certificate will no longer be in the PKCS#12 format needed for this step* [cite: 11].
4. Send the certificate to **Yujun Wu** (`yujun@fnal.gov`) or **Dmitry O Litvintsev** (`litvinse@fnal.gov`) to verify the setup [cite: 16].

### 3. Software Installation
Install `osg-ca-certs` and `osg-client` on your machine; you may need assistance from your Systems group [cite: 12].
- **With Root Access:** Instructions are available at [IU Twiki OSG Client](https://twiki.grid.iu.edu/bin/view/Documentation/Release3/InstallOSGClient#6_2_Stopping_and_Disabling_Servi) [cite: 13].
- **Without Root Access (Regular Users):** Use the [OSG Tarball option](https://twiki.grid.iu.edu/bin/view/Documentation/Release3/InstallOSGClientTarball) [cite: 14, 15].

---

## Configuration and Initialization

1. **Set Globus Environment:**
   Run the following command to ensure the correct version of Globus:
   ```bash
   . /opt/globus-5.2.5/etc/globus-user-env.sh
   ``` [cite: 17]
2. **Initialize Grid Proxy:**
   Initialize a proxy valid for 168 hours (one week):
   ```bash
   grid-proxy-init -valid 168:0
   ``` [cite: 18]

---

## Data Download Steps

### 1. Test Connectivity
Test if the download is working using the following command:
```bash
globus-url-copy -vb -dbg -nodcau gsiftp://fndca1.fnal.gov:2811//temp/testfnal.txt file:////tmp/testfile
``` [cite: 19, 20]

### 2. Retrieve File List
Copy the `COMPLETE_FILE_LISTING` file to your directory:
```bash
globus-url-copy gsiftp://fndca1.fnal.gov/COMPLETE_FILE_LISTING file:////`pwd`/COMPLETE_FILE_LISTING
``` [cite: 21, 22]

### 3. Bulk Download
Copy the script `complete.sh` into the same folder as the listing file and run it [cite: 23, 24].

**Script: `complete.sh`**
```bash
#!/bin/bash
cat COMPLETE_FILE_LISTING | grep SGDP | while read path size cksum
do
    globus-url-copy -c -vb -nodcau -cd -bs 2000000 -sync gsiftp://fndca1.fnal.gov${path} file:////`pwd`/${path}
done
``` [cite: 25, 26, 27, 28, 29, 30, 31]

---

## Performance Optimization (Optional)

Transfers are faster if parallel streams are enabled [cite: 32].

1. **Firewall Settings:**
   Request your network administrator to open ports **50000-50100** [cite: 33, 37].
2. **Environment Variables:**
   Set the following:
   ```bash
   export GLOBUS_TCP_PORT_RANGE=50000,50100
   export GLOBUS_HOSTNAME=[Name_of_the_external_IP]
   ``` [cite: 34, 35, 36]
3. **Command Update:**
   Add `-p 10` to the options in your `globus-url-copy` command [cite: 38].
