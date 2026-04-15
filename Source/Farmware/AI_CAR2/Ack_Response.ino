
#define STX 0xEA
#define ETX 0x03
 
byte ACK_buff[10] = {};

byte Error_Code = 0;

float BAT_Voltage;
byte make_checksum(byte* b)
{
  int i=0;
  byte cs = 0;

  for ( i=1 ; i<=5 ; i++)
  {
    cs += *(b+i);
  }
  return ( (~cs) + 1 ) ;
}

void Ack_Response(int steering_value, int speed_value, int Dummy_1, int Dummy_2)
{
  //printf0("\r\n < Ack_Response > \r\n");

  byte length = 0x03;

  ACK_buff[0] = (byte)STX;
  ACK_buff[1] = (byte)length;

  ACK_buff[2] = (byte)steering_value;
  ACK_buff[3] = (byte)speed_value;
  ACK_buff[4] = (byte)Dummy_1;  
  ACK_buff[5] = (byte)Dummy_2;

  ACK_buff[6] = (byte)make_checksum(&ACK_buff[0]); // C/S
  ACK_buff[7] = (byte)ETX;

  byte i = 0;
  for ( i=0 ; i<=7 ; i++ )
  {
    usart0_putch(ACK_buff[i]);  
  }
}
