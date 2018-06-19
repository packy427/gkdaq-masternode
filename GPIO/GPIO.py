

class AdafruitBBIOAdapter(BaseGPIO):
    """GPIO implementation for the Beaglebone Black using the Adafruit_BBIO
    library.
    """

    def __init__(self, bbio_gpio):
        self.bbio_gpio = bbio_gpio
        # Define mapping of Adafruit GPIO library constants to RPi.GPIO constants.
        self._dir_mapping = { OUT:      bbio_gpio.OUT,
                              IN:       bbio_gpio.IN }
        self._pud_mapping = { PUD_OFF:  bbio_gpio.PUD_OFF,
                              PUD_DOWN: bbio_gpio.PUD_DOWN,
                              PUD_UP:   bbio_gpio.PUD_UP }
        self._edge_mapping = { RISING:  bbio_gpio.RISING,
                               FALLING: bbio_gpio.FALLING,
                               BOTH:    bbio_gpio.BOTH }

    def setup(self, pin, mode, pull_up_down=PUD_OFF):
        """Set the input or output mode for a specified pin.  Mode should be
        either OUTPUT or INPUT.
        """
        self.bbio_gpio.setup(pin, self._dir_mapping[mode],
                             pull_up_down=self._pud_mapping[pull_up_down])

    def output(self, pin, value):
        """Set the specified pin the provided high/low value.  Value should be
        either HIGH/LOW or a boolean (true = high).
        """
        self.bbio_gpio.output(pin, value)

    def input(self, pin):
        """Read the specified pin and return HIGH/true if the pin is pulled high,
        or LOW/false if pulled low.
        """
        return self.bbio_gpio.input(pin)

    def input_pins(self, pins):
        """Read multiple pins specified in the given list and return list of pin values
        GPIO.HIGH/True if the pin is pulled high, or GPIO.LOW/False if pulled low.
        """
        # maybe bbb has a mass read...  it would be more efficient to use it if it exists
        return [self.bbio_gpio.input(pin) for pin in pins]

    def add_event_detect(self, pin, edge, callback=None, bouncetime=-1):
        """Enable edge detection events for a particular GPIO channel.  Pin 
        should be type IN.  Edge must be RISING, FALLING or BOTH.  Callback is a
        function for the event.  Bouncetime is switch bounce timeout in ms for 
        callback
        """
        kwargs = {}
        if callback:
            kwargs['callback']=callback
        if bouncetime > 0:
            kwargs['bouncetime']=bouncetime
        self.bbio_gpio.add_event_detect(pin, self._edge_mapping[edge], **kwargs)

    def remove_event_detect(self, pin):
        """Remove edge detection for a particular GPIO channel.  Pin should be
        type IN.
        """
        self.bbio_gpio.remove_event_detect(pin)

    def add_event_callback(self, pin, callback, bouncetime=-1):
        """Add a callback for an event already defined using add_event_detect().
        Pin should be type IN.  Bouncetime is switch bounce timeout in ms for 
        callback
        """
        kwargs = {}
        if bouncetime > 0:
            kwargs['bouncetime']=bouncetime
        self.bbio_gpio.add_event_callback(pin, callback, **kwargs)

    def event_detected(self, pin):
        """Returns True if an edge has occured on a given GPIO.  You need to 
        enable edge detection using add_event_detect() first.   Pin should be 
        type IN.
        """
        return self.bbio_gpio.event_detected(pin)

    def wait_for_edge(self, pin, edge):
        """Wait for an edge.   Pin should be type IN.  Edge must be RISING, 
        FALLING or BOTH.
        """
        self.bbio_gpio.wait_for_edge(pin, self._edge_mapping[edge])

    def cleanup(self, pin=None):
        """Clean up GPIO event detection for specific pin, or all pins if none 
        is specified.
        """
        if pin is None:
            self.bbio_gpio.cleanup()
        else:
            self.bbio_gpio.cleanup(pin)

class AdafruitMinnowAdapter(BaseGPIO):
    """GPIO implementation for the Minnowboard + MAX using the mraa library"""
    
    def __init__(self,mraa_gpio):
        self.mraa_gpio = mraa_gpio
        # Define mapping of Adafruit GPIO library constants to mraa constants
        self._dir_mapping = { OUT:      self.mraa_gpio.DIR_OUT,
                              IN:       self.mraa_gpio.DIR_IN }
        self._pud_mapping = { PUD_OFF:  self.mraa_gpio.MODE_STRONG,
                              PUD_UP:   self.mraa_gpio.MODE_HIZ,
                              PUD_DOWN: self.mraa_gpio.MODE_PULLDOWN }
        self._edge_mapping = { RISING:   self.mraa_gpio.EDGE_RISING,
                              FALLING:  self.mraa_gpio.EDGE_FALLING,
                              BOTH:     self.mraa_gpio.EDGE_BOTH }

    def setup(self,pin,mode):
        """Set the input or output mode for a specified pin.  Mode should be
        either DIR_IN or DIR_OUT.
        """
        self.mraa_gpio.Gpio.dir(self.mraa_gpio.Gpio(pin),self._dir_mapping[mode])   

    def output(self,pin,value):
        """Set the specified pin the provided high/low value.  Value should be
        either 1 (ON or HIGH), or 0 (OFF or LOW) or a boolean.
        """
        self.mraa_gpio.Gpio.write(self.mraa_gpio.Gpio(pin), value)
    
    def input(self,pin):
        """Read the specified pin and return HIGH/true if the pin is pulled high,
        or LOW/false if pulled low.
        """
        return self.mraa_gpio.Gpio.read(self.mraa_gpio.Gpio(pin))    
    
    def add_event_detect(self, pin, edge, callback=None, bouncetime=-1):
        """Enable edge detection events for a particular GPIO channel.  Pin 
        should be type IN.  Edge must be RISING, FALLING or BOTH.  Callback is a
        function for the event.  Bouncetime is switch bounce timeout in ms for 
        callback
        """
        kwargs = {}
        if callback:
            kwargs['callback']=callback
        if bouncetime > 0:
            kwargs['bouncetime']=bouncetime
        self.mraa_gpio.Gpio.isr(self.mraa_gpio.Gpio(pin), self._edge_mapping[edge], **kwargs)

    def remove_event_detect(self, pin):
        """Remove edge detection for a particular GPIO channel.  Pin should be
        type IN.
        """
        self.mraa_gpio.Gpio.isrExit(self.mraa_gpio.Gpio(pin))

    def wait_for_edge(self, pin, edge):
        """Wait for an edge.   Pin should be type IN.  Edge must be RISING, 
        FALLING or BOTH.
        """
        self.bbio_gpio.wait_for_edge(self.mraa_gpio.Gpio(pin), self._edge_mapping[edge])

def get_platform_gpio(**keywords):
    """Attempt to return a GPIO instance for the platform which the code is being
    executed on.  Currently supports only the Raspberry Pi using the RPi.GPIO
    library and Beaglebone Black using the Adafruit_BBIO library.  Will throw an
    exception if a GPIO instance can't be created for the current platform.  The
    returned GPIO object is an instance of BaseGPIO.
    """

    import RPi.GPIO
    return RPiGPIOAdapter(RPi.GPIO, **keywords)
