import machine, time 
i2c = machine.I2C(0 ,scl = machine.Pin (1) ,sda = machine.Pin (0))
devices = i2c.scan()
print(devices)


def unpack ( buffer ):
    """ Unpacks MSB - ordered buffer of bytes into an unsigned integer .
    Note : buffer must be a bytes - like object or a list of integers in the
    range [0 , 255].
    Usage :
    >>> unpack ([0 x01 , 0 x00 ])
    256
    >>> unpack ([0 x10 , 0 x00 ])
    4096
    >>> unpack ([0 xFF , 0 xFF , 0 xFF ])
    16777215
    """
    _buffer = reversed ( bytearray ( buffer ))
    return sum ( _byte << ( _i * 8) for _i , _byte in enumerate ( _buffer ))

registry_positions = [0xA2,0xA4,0xA6,0xA8,0xAA,0xAC]
cbytes=[i2c.readfrom_mem(119,poss,2) for poss in registry_positions]

#c1bytes = i2c.readfrom_mem ( 119 , 0xA2 , 2)
#c1 = (c1bytes [0] << 8) + c1bytes [1]
#c2 = unpack ( c1bytes )

cbytes_ = [unpack(constant) for constant in cbytes]
print(cbytes_)

c1 = (cbytes[0][0]<<8) + cbytes[0][1]
c2 = (cbytes[1][0]<<8) + cbytes[1][1]
c3 = (cbytes[2][0]<<8) + cbytes[2][1]
c4 = (cbytes[3][0]<<8) + cbytes[3][1]
c5 = (cbytes[4][0]<<8) + cbytes[4][1]
c6 = (cbytes[5][0]<<8) + cbytes[5][1]

print(c1,c2,c3,c4,c5,c6)
###ADC

while True:

    TEMPERATURE_ADC =  b'\x48'
    PRESSURE_ADC = b'\x58'
    # send temperature ADC command and pause for response
    i2c.writeto(119 , TEMPERATURE_ADC)
    time.sleep_ms (500)
    t_adc_bytes = i2c.readfrom_mem(119 ,0x00 ,3)

    i2c.writeto(119 , PRESSURE_ADC )
    time.sleep_ms (500)
    # read the temperature ADC values
    P_adc_bytes = i2c.readfrom_mem(119 ,0x00 ,3)
    # unpack value as integer
    D2 = unpack(t_adc_bytes)  #unpacked temperature ref datasheet
    D1 = unpack(P_adc_bytes) # unpacked pressure

    #print(t_adc,P_adc)

    ############################################################################################################################

    dt = D2 - cbytes_[4]*(2**8)
    TEMP = 2000+dt*cbytes_[5]/(2**23)
    print(D1,D2,dt)
    print(f'Measured temperature is {TEMP/100 :2.2f} °C')

    OFF = cbytes_[1]*(2**16)+(cbytes_[3]*dt)/(2**7)
    SENS = cbytes_[0]*(2**15)+(cbytes_[2]*dt)/(2**8)
    P = (D1*SENS/(2**21)-OFF)/(2**15)

    print(f'Measured pressure is {P/100 :2.2f} millibars')
    
    
