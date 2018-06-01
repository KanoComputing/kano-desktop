Feature: Touchscreen flipping

    Scenario: The OS boots up to Overture
        Given An OS which has not booted before
         When Overture is running
         Then Touching touch-sensitive elements works
         
    Scenario: The OS is flipped and boots up to Overture
        Given An OS which has booted before
          And configured for the screen to be flipped
         When Overture is running (eg, a new user)
         Then Touching touch-sensitive elements works

    Scenario: The OS is configured not to be flipped
        Given An OS which has been configured to be flipped
          And It is configured for the screen no longer to be flipped
         When Overture is running (eg, a new user)
         Then Touching touch-sensitive elements works

    Scenario: Dashboard when the OS is configured not to be flipped
        Given An OS which has not been configured to be flipped
         When Dashboard is running (eg, a new user)
         Then Touching touch-sensitive elements works

    Scenario: Classic mode when the OS is configured not to be flipped
        Given An OS which has not been configured to be flipped
         When Classic mode is running (eg, a new user)
         Then Touching touch-sensitive elements works

    Scenario: Dashboard when the OS is configured to be flipped
        Given An OS which has been configured to be flipped
         When Dashboard is running (eg, a new user)
         Then Touching touch-sensitive elements works

    Scenario: Classic mode when the OS is configured to be flipped
        Given An OS which has been configured to be flipped
         When Classic mode is running (eg, a new user)
         Then Touching touch-sensitive elements works

         
