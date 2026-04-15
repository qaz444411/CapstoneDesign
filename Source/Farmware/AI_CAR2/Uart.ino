



#define COM_0  0


#define _MAX_BUFF_LEN_    128
#define _MAX_CH_      2

#define END_OF_STR    '\0'
#define _BS   0x08
#define _CR   0x0D
#define _ESC  0x1B

#define _STX  0xEA  //Ohm
#define _ETX  0x03  //End of Text

#define _Motor_ID_STX  0x01
#define _Motor_ID_STX  0x02




byte Rx0_Buffer[_MAX_BUFF_LEN_];
byte Rx0_Index = 0;
byte Rx0_Complete = 0;

void Uart_init()
{
  Init_USART_Buf0();
  Init_USART(COM_0, 115200L); // USB_Connect + NX Carrier/ R470
}

void Init_USART_Buf0(void)
{
  //memset(void *, int, size_t)
  memset(Rx0_Buffer, 0 , sizeof(Rx0_Buffer) );
}




void Init_USART(byte usart_ch, long baudrate)
{
  // n is '0' or '1'
  //-----<USART Control and Status Register A_B_C>-----//
  
    //UCSRnA ----- [7]RXCn  [6]TXCn  [5]UDREn  [4]FEn(프레임오류)  [3]DORn(데이터 오버런)  [2]UPEn  [1]U2Xn  [0]MPCMn // //
    //Init Value ---- 0010_0000
    
    //UCSRnB ----- [7]RXCIEn  [6]TXCIEn  [5]UDRIEn  [4]RXENn  [3]TXENn  [2]UCSZn2  [1]RXB8n  [0]TXB8n  
    //Init Value ---- 0010_0000
    
    //UCSRnC -----[7]  -  [6]UMSELn  [5]UPMn1  [4]UPMn0  [3]USBSn  [2]UCSZn1  [1]UCSZn0  [0]UCPOLn
    //Init Value ---- 0000_0110

    //UCPOLn --->>> 0 : Rx/Tx Rising Edge , 1 : Rx/Tx Falling Edge
    //UCSZn[2:0] --->>>  000 : 5Bit , 001 : 6Bit , 010 : 7Bit , 011 : 8bit , 111 : 9Bit 
  
  switch(usart_ch)
  {
    case COM_0:
      UCSR0A = 0x00;
      //UCSR0B |= _BV(RXCIE0) | _BV(TXCIE0) | _BV(RXEN0) | _BV(TXEN0); 
      //UCSR0B |= _BV(RXEN0) | _BV(TXEN0);
      UCSR0B |= _BV(RXEN0) | _BV(TXEN0) | _BV(RXCIE0);
      UCSR0C = _BV(UCSZ01) | _BV(UCSZ00);    //전송문자 - 8Bit
      break; 
  }
  SetBaudRate(usart_ch, baudrate);
}

void SetBaudRate(byte usart_ch, unsigned long baud)
{
  word ubrr_value;        //Usart Baud Rate Reg  
  ubrr_value = (16000000 /(baud*8L))-1; 
  switch(usart_ch)
  {
    case COM_0:
      UCSR0A |= _BV(U2X0);        //Double Speed            
      UBRR0H = (byte) (ubrr_value >> 8);
      UBRR0L = (byte) (ubrr_value & 0xff);
      break;
  }
}


SIGNAL(USART0_RX_vect)
{
  byte Rx0_Temp;
  byte checksum_temp;
  byte *ptr;
  byte length;
  Rx0_Temp = UDR0;
  //usart0_putch(Rx0_Temp);
  //usart0_putch(0x41);
  
  switch(Rx0_Temp)
  {
    case _BS:
      if( Rx0_Index != 0 )
      {
        Rx0_Index--;
        Rx0_Buffer[Rx0_Index] = 0;
        usart0_TxStr( "\b \b" );
      }
    break;
    case _CR:
      if(Rx0_Index != 0)
      {
        Rx0_Complete = 1;
        //dbg_cmd_index = 0;
      }
    else
    {
      usart0_TxStr("\r\n>");
    }
    break;
    case _ESC:
    
    default:
    if(Rx0_Index >= _MAX_BUFF_LEN_)
    {
      Rx0_Index = 0;
      break;
    }
    
    Rx0_Buffer[Rx0_Index] = Rx0_Temp;
                                                      
    //usart0_putch(Rx0_Temp);

    if (Rx0_Buffer[Rx0_Index]==_ETX)
    {
      signed char idx = Rx0_Index;   //index
      //signed char loop_cnt = idx+1;
      
      //usart0_TxStr("\r\n _ETX");
      //printf0("\r\nidx = %d\r\n",idx);
      
      for( ; idx>= (0); idx--)
      {
        ptr = &Rx0_Buffer[idx];
        //printf0("==Rx[%d]=0x%x\r\n",idx,*ptr);
        
        if( *ptr == _STX)
        {
          length =*(ptr+1); //data length value
          //usart0_putch(length); //03
          //printf0("\r\n\t[1]length = %d",length );
        }
        
        if( (*ptr ==_STX) && ( *(ptr + 1 + 1 + length + 1 +1 ) == _ETX ) )//STX + CMD + LENGTH + DATA[N] + CS + ETX
        { 
          //usart0_putch(*ptr);                      
          //usart0_putch(*(ptr + 1 + 1 + length + 1 +1 ));
          byte length_index;
          byte cs_index;
          
          //printf0("\r\n\t[2]-----idx = %d",idx);
          //usart0_putch(idx);
          length_index = idx+1;
          //usart0_putch(Rx0_Buffer[length_index]);
          //usart0_putch(length_index);
          //printf0("\r\n\t[3]length_index = %d",length_index);
          cs_index = length_index + 1 + length + 1;
          //printf0("\r\n\t[4]cs_index = %d",cs_index);
          //usart0_putch(Rx0_Buffer[cs_index]);
          //checksum_temp = checksum(length_index , cs_index,  &Rx0_Buffer[idx] );
          checksum_temp = checksum(length_index , cs_index,  &Rx0_Buffer[0] );
          //usart0_putch(checksum_temp);
          //printf0("\r\n\t[5]checksum_temp = 0x%x",checksum_temp );
          //printf0("\r\n\t[6]checksum = 0x%x\r\n", Rx0_Buffer[idx + 1 + 1 + length + 1] );

          //printf0("\r\n\t[7]Rx0_Buffer[CS] = 0x%x\r\n", Rx0_Buffer[cs_index] );
          //if (checksum_temp == Rx0_Buffer[idx + 1 + 1 + length + 1] )       //STX + CMD + LENGTH + DATA[N] + CS
          //if(checksum_temp == Rx0_Buffer[cs_index] )       //STX + CMD + LENGTH + DATA[N] + CS
          
          //if (checksum_temp == Rx0_Buffer[idx + 1 + length + 1] )
          if(checksum_temp == Rx0_Buffer[cs_index] )
          {
            Rx_Frame.complete = 1;
            Rx_Frame.length =          Rx0_Buffer[idx+1]; 
            //usart0_putch(Rx0_Buffer[idx+1]);     
            Rx_Frame.steering_value =  Rx0_Buffer[idx+1+1];
            //usart0_putch(Rx0_Buffer[idx+1+1]);
            Rx_Frame.speed_value =     Rx0_Buffer[idx+1+1+1];    
            //usart0_putch(Rx0_Buffer[idx+1+1+1]);
            if(Rx_Frame.length != 0)
            {
              Rx_Frame.data = Rx0_Buffer[idx+1+1];
            }
            Init_USART_Buf0();
            
            Rx0_Index = 0;
            break;
          }
        }
      }
    }
    Rx0_Index++;
    break;
  }  
}

//////////////////////////////////////////////////////////////////////

byte checksum(char cmd_idx, char cs_idx, byte *buff)   
{
  byte ret_cs = 0;
  char i = cmd_idx;
  for( ; i <cs_idx; i++)
  {
    ret_cs += *(buff+i);
  } 
  ret_cs = (~(ret_cs))+1;
  //usart0_putch(ret_cs); 
  
  return ret_cs;
}



void usart0_putch(char data )
{
  while(!( UCSR0A & (1<<UDRE0)));
  UDR0 = data;
}
void usart0_TxStr(char *str )
{
  unsigned int i = 0;
  while( *(str + i) != 0 )
  {
    usart0_putch( *(str+i) );
    i++;
  }
}
void printf0(char *fmt , ...)
{
  va_list ap;
  char string[_MAX_BUFF_LEN_];

  va_start(ap,fmt);
  vsprintf(string,fmt,ap);

  usart0_TxStr(string);

  va_end(ap);
}
