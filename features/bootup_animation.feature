Feature: Boot Animation

    Scenario: The OS boots up to Overture
        Given An OS which has not booted before
         When The OS is booted
         Then The boot animation displays
          And The boot animation stops before overture

    Scenario: The OS boots up to dashboard
        Given An OS which has booted before and gone through overture
         When The OS is booted
         Then The boot animation displays
          And The boot animation stops before the dashboard startup animation

    Scenario: The OS is updated from 3.14 or 3.14.1
        Given An OS which is on version 3.14 or 3.14.1
         When The OS is updated to 3.15 or later
         Then The 'init=/usr/bin/kano-os-loader' statement is removed from /boot/cmdline.txt
          And The boot animation displays
          And The boot animation stops before the dashboard startup animation


