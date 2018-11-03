# Digital Vacuum Regulator with RPi
![1](https://github.com/sbkirby/RPi_vacuum_gauge/blob/master/images/main_photo_1.jpg)![2](https://github.com/sbkirby/RPi_vacuum_gauge/blob/master/images/main_photo_2.jpg)

This is a Veneer Vacuum Press (Vacuum Pump) which has been modified with a Digital Vacuum Regulator to operate with a selectable vacuum pressure. This device is a replacement for the Vacuum Controller in my DIY Veneer Vacuum Press built with plans from [VeneerSupplies.com](https://www.veneersupplies.com/) or [JoeWoodworking.com](http://www.joewoodworker.com/). These are great plans and the pumps operate very satisfactorily as designed. However, I'm a tinkerer, and I wanted to enhance my pump with the ability to easily and readily control the pressure settings (without a screw driver) over a wider range of pressures with a digitally controlled regulator.

Recently, a need arose which was beyond the lower limits of my Vacuum Controller (Type 1). This project required a Type 2-Vacuum Controller for pressures in the range of 2 to 10 in-Hg. Replacing my Type 1-Vacuum Controller with a Type 2 model was an option, however, this seemed impractical since it would require an additional cost and modifications to switch between the two vacuum ranges. The ideal solution is a single controller with a wider range of pressures (2 to 28 in-Hg).

**Vacuum Controller:** A vacuum controlled micro-switch used to activate a vacuum pump or relay at a selected pressure. The vacuum controller has an adjustment screw that allows you to dial in your desired level of vacuum. The contacts are rated at 10 amps at 120v AC.

### Types of Vacuum Controller
* Type 1 = adjustable for 10.5" to 28" of Hg (Differential 2 to 5" of Hg)
* Type 2 = adjustable for 2" to 10" of Hg (Differential 2 to 4" of Hg)

## Design Considerations
![Main Control Box Wiring Diagram](https://github.com/sbkirby/RPi_vacuum_gauge/blob/master/images/main_control_box_wiring_diagram.jpg)

My design replaces the Vacuum Controller with a Digital Vacuum Regulator (DVR). The DVR will be used to control the LINE-DVR line of the RELAY-30A as seen in the Main Control Box schematic. This design requires the addition of a AC/DC 5-VDC Power Supply to Main Control Box for powering the DVR.

This design is capable of maintaining a wide range of vacuum pressures, but the performance is entirely dependent upon the capability of the pump. At the lower pressure range a large CFM pump will maintain these pressures, but result in larger differential pressure swings as a result of the displacement of the pump. This is the case for my 3 CFM pump. It is capable of maintaining 3 in-Hg, but the differential pressure swing is ±1 in-Hg, and the ON cycles of the pump, although infrequent, last approximately one or two seconds. A differential pressure swing of ±1 in-Hg will result with pressures between 141 lbs/ft² to 283 lbs/ft². I have no experience vacuum pressing at these low pressures, therefore I am not sure of the significance of this differential pressure swing. In my opinion, a smaller CFM vacuum pump would probably be more appropriate to maintain these lower vacuum pressures and reduce the differential pressure swings.

The construction of this regulator includes a Raspberry Pi Zero, MD-PS002 Pressure Sensor, HX711 Wheatstone Bridge Amplifier Module, LCD Display, 5V Power Supply, Rotary Encoder and a Relay Module. All of these parts are available from your favorite internet electronics parts suppliers.

I choose a Raspberry Pi (RPi) because python is my preferred programming language, and the support for RPi's is readily available. I am confident this application could be ported to an ESP8266 or other controllers capable of running python. The one disadvantage of the RPi is a Shutdown is highly recommended before powering it down to prevent corruption of the SD Card.

## Parts List

This device is constructed with off the shelf parts including a Raspberry Pi, Pressure Sensor, HX711 Bridge Amplifier, LCD and other parts costing approximately $25.

**PARTS:** 
* 1ea Raspberry Pi Zero - Version 1.3 $5 
* 1ea MD-PS002 Vacuum Sensor Absolute Pressure Sensor $1.75 
* 1ea HX711 Load Cell and Pressure sensor 24 bit AD module $0.75 
* 1ea KY-040 Rotary Encoder Module $1 
* 1ea 5V 1.5A 7.5W Switch Power Module 220V AC-DC Step Down Module $2.56 
* 1ea 2004 20x4 Character LCD Display Module $4.02 
* 1ea 5V 1-Channel Optocoupler Relay Module $0.99 
* 1ea Adafruit Perma-Proto Half-sized Breadboard PCB $4.50 
* 1ea 2N2222A NPN Transistor $0.09 
* 2ea 10K Resistors 
* 1ea Hose Barb Adapter 1/4" ID x 1/4" FIP $3.11 
* 1ea Brass Pipe Square Head Plug 1/4" MIP $2.96 
* 1ea GX12-2 2 Pin Diameter 12mm Male & Female Wire 
* Panel Connector Circular Screw Type Electrical Connector Socket Plug $0.67 
* 1ea Proto Box (or 3D Printed)

## Vacuum Sensor Assembly
![Vacuum Sensor Diagram](https://github.com/sbkirby/RPi_vacuum_gauge/blob/master/images/vacuum_sensor_diagram.jpg)

The MD-PS002 pressure sensor manufactured by Mingdong Technology (Shanghai) Co., Ltd. (MIND) has a range of 150 KPa (absolute pressure). The gauge pressure range (at sea level) for this sensor would be 49 to -101 KPa or 14.5 to -29.6 in-Hg. These sensors are readily available on eBay, banggood, aliexpress and other online sites. However, the specifications listed by a few of these suppliers are conflicting, therefore, I've included a translated "Technical Parameters" sheet from a Mingdong Technology.

![Vacuum Sensor Assembly](https://github.com/sbkirby/RPi_vacuum_gauge/blob/master/images/vacuum_sensor_assembly_1.jpg)

Connecting the sensor to a HX711 Load Cell and Pressure sensor 24 bit AD module requires the following: connect Pins 3 & 4 together; Pin 1 (+IN) to E+; Pin 3 & 4 (-IN) to E-; Pin 2 (+OUT) to A+ and Pin 5 (-OUT) to A- of the HX711 module. Prior to packaging the wired sensor in a brass adapter, cover the leads and the exposed edges of the sensor with heat shrink tubing or electrical tape. Insert and center the sensor over the barbed nipple opening, and then use clear silicone caulking to seal the sensor inside the adapter while taking care to keep the caulking away from the sensor face. A Brass Pipe Square Head Plug which has been drilled with a hole large enough to accommodate the sensor wire is threaded over the wire, filled with silicone caulking and screwed onto the barbed adapter. Wipe excess caulking from the assembly, and wait 24 hours for the caulking to dry before testing.

![MD-PS002 Data Sheet](https://github.com/sbkirby/RPi_vacuum_gauge/blob/master/images/md-ps002_data_sheet.jpg)

## Electronics Assembly
![Main Wiring Diagram](https://github.com/sbkirby/RPi_vacuum_gauge/blob/master/images/vacuum_sensor_diagram_main.jpg)

The electronics consist of a Raspberry Pi Zero (RPi) connected to an HX711 module with a MD-PS002 pressure sensor, KY-040 Rotary Encoder, Relay Module and a LCD display. The Rotary Encoder is interfaced to the RPi via Pin 21 to the DT of the encoder, Pin 16 to the CLK and Pin 20 to the SW or switch of the encoder. The pressure sensor is connected to the HX711 module, and the DT and SCK pins of this module are connected directly to Pin 5 and 6 of the RPi. The Relay Module is triggered by a 2N2222A transistor circuit which is connected to RPi Pin 32 for a trigger source. The Normally Open contacts of the Relay Module are connected to LINE-SW and one side of the coil of the 30A RELAY. Power and Ground for the Digital Vacuum Regulator are supplied by Pins 1, 4, 6 and 9 of the RPi. Pin 4 is the 5v power pin, which is connected directly to the RPi's power input. Details of the connections can be seen in the Digital Vacuum Regulator schematic.

![Bud Box Inside](https://github.com/sbkirby/RPi_vacuum_gauge/blob/master/images/bud_box_inside.jpg)

## Update and Configure the Raspberry Pi
![raspi-config](https://github.com/sbkirby/RPi_vacuum_gauge/blob/master/images/raspi-config.jpg)

Update the existing software on your Raspberry Pi (RPi) with the following command lines instructions
```
sudo apt-get update
sudo apt-get upgrade
```
Depending on how out-of-date your RPi is at the time will determine the amount of time needed to complete these commands.
Next, the RPi needs to be configured for I2C communications via Raspi-Config.
```
sudo raspi-config
```
The screen seen above will appear. First select Advanced Options and then Expand Filesystem and select Yes. After returning to the Main Menu of Raspi-Config select Enable Boot to Desktop/Scratch and choose to Boot to Console. From the Main Menu select Advanced Options, and enable I2C and SSH from the available options. Finally, select Finish and reboot the RPi.

## Software
Log into the RPi and create the following directories. The /Vac_Sensor contains the program files and /logs will contain the crontab log files.
```
cd ~
mkdir Vac_Sensor
mkdir logs
cd Vac_Sensor
```
Copy the files above to the /Vac_Sensor folder. I use WinSCP to connect and manage the files on the RPi. Connection to the RPi maybe done via Wifi or serial connection, but SSH needs be enabled in raspi-config to allow this type of connection.

The primary program is vac_sensor.py and may be run from the command prompt. In order to test the script enter the following:
```
sudo python vac_sensor.py
```
As mentioned previously, the vac_sensor.py script is the primary file for the scale. It imports the hx711.py file to read the vacuum sensor via HX711 module. The version of hx711.py used for my project comes from [tatobari/hx711py](https://github.com/tatobari/hx711py). I found this version provided the features I wanted.

The LCD requires the RPi_I2C_driver.py by Denis Pleic and forked by Marty Tremblay, and can be found at [MartyTremblay/RPi_I2C_driver.py](https://gist.github.com/MartyTremblay/7a7fbf76c0c93734511b).

Rotary Encoder by Peter Flocker can be found at [https://github.com/petervflocke/rotaryencoder_rpi](https://github.com/petervflocke/rotaryencoder_rpi)

pimenu by Alan Aufderheide can be found at [https://github.com/skuater/pimenu](https://github.com/skuater/pimenu)

The config.json file contains the data stored by the program, and some items can be modified by menu options. This file is updated and saved at Shutdown. The "units" can be setup via the Units menu option either as in-Hg (default), mm-Hg or psi. The "vacuum_set" is the cutoff pressure, and is stored as in-Hg value, and is modified by the Cutoff Pressure menu option. A "calibration_factor" value is manually set in the config.json file, and is determined by calibrating the vacuum sensor to a vacuum gauge. The "offset" is value created by Tare, and can be set via this menu option. The "cutoff_range" is manually set in the config.json file, and is the differential pressure range of the "vacuum_set" value.

Cutoff Value = "vacuum_set" ± (("cutoff_range"/100) x "vacuum_set")

Please note your "calibration_factor" and "offset" may differ from those I have. Example config.json file:
```
{"units": 0, "vacuum_set": -15.0, "calibration_factor": 230000, "cutoff_range": 0.5, "offset": 11448294}
```

## Calibration
![Calibration Gauge](https://github.com/sbkirby/RPi_vacuum_gauge/blob/master/images/calibration_gauge.jpg)

Calibration is much easier to do using SSH and running the following commands:
```
cd Vac_Sensor 
sudo python vac_sensor.py
```
Exiting the python script can be done via Ctrl-C, and modifications can be made to the /Vac_Sensor/config.json file.

Calibrating the vacuum sensor requires an accurate vacuum gauge, and adjusting the "calibration_factor" to match the output displayed on the LCD. First, use the Tare menu option to set and save the "offset" value with the pump at atmospheric pressure. Next, turn the pump ON with the Vacuum menu and after the pressure settles read the LCD display and compare this to vacuum gauge. Turn the pump OFF and Exit the script. Adjust the "calibration_factor" variable located in /Vac_Sensor/config.json file. Restart the script and repeat the process with exception of Tare. Make the necessary adjustments to the "calibration_factor" until the LCD display matches the gauge reading.

The "calibration_factor" and "offset" affect the display via the following calculations:

get_value = read_average - "offset"

pressure = get_value/"calibration_factor"

I used an old Peerless Engine Vacuum Gauge to calibrate the regulator instead of the vacuum gauge on my pump because it had been knocked out calibration. The Peerless gauge is 3-3/4" (9.5 cm) in diameter and much easier to read.

## Run at Startup
![Crontab](https://github.com/sbkirby/RPi_vacuum_gauge/blob/master/images/crontab.jpg)

There's an excellent Instructable [Raspberry Pi: Launch Python script on startup](https://www.instructables.com/id/Raspberry-Pi-Launch-Python-script-on-startup/?ALLSTEPS) for running a scripts at startup.

Log into the RPi and change to the /Vac_Sensor directory.
```
cd /Vac_Sensor
nano launcher.sh
```
Include the following text in launcher.sh
```
#!/bin/sh
# launcher.sh
# navigate to home directory, then to this directory, then execute python script, then back home
cd /
cd home/pi/Vac_Sensor
sudo python vac_sensor.py
cd /
```
Exit and save the launcher.sh

We need to make the script an executable.
```
chmod 755 launcher.sh
```
Test the script.
```
sh launcher.sh
```
Next, we need to edit crontab (the linux task manager) to launch the script at startup. Note: we have already created the /logs directory previously.
```
sudo crontab -e
```
This will bring the crontab window as seen above. Navigate to the end of the file and enter the following line.
```
@reboot sh /home/pi/Vac_Sensor/launcher.sh >/home/pi/logs/cronlog 2>&1
```
Exit and save the file, and reboot the RPi. The script should start the vac_sensor.py script after the RPi reboots. The status of the script can be checked in the log files located in the /logs folder.
