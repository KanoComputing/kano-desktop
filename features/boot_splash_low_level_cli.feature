Feature: Boot splash low level cli

    Scenario: The command is executed with no arguments
        Given the command `kano-boot-splash-cli` is executed
         Then its command options are printed

    Scenario: A different image is set by the command line 
        Given the OS boots normally
         And it has already gone through overture
        When the command `sudo kano-boot-splash-cli set /path/to/image.png` is run
         And the os is then rebooted
         And /path/to/image.png is a valid png image
        Then the image is displayed on boot
         And the image is removed before the dashboard loading image is displayed.

    Scenario: A different image is set by the command line, but then removed
        Given the OS boots normally
         And it has already gone through overture
        When the command `sudo kano-boot-splash-cli set /path/to/image.png` is run
         And subsequently the command `sudo kano-boot-splash-cli clear` is run
         And the os is then rebooted
        Then the normal boot animation is displayed on boot
         And the boot animation is removed before the dashboard loading image is displayed.

# Note that the updater will run kano-boot-splash-cli clear