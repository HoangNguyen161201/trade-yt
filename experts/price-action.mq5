#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"


int OnInit()
{
    // Bật timer, 1 giây gọi OnTimer 1 lần
    EventSetTimer(1);
    
    return(INIT_SUCCEEDED);
}

void OnTick()
{
   int bars = 180;  
   datetime last_time = 0;
   WriteCandle("candle-m15.txt", PERIOD_M15, 180, 0);
   WriteCandle("candle-m5.txt", PERIOD_M5, 180, 0);
}

void OnTimer()
{
    // vào đây đọc file
    string file_name = "price-action.txt";
    int file_handle = FileOpen("price-action.txt", FILE_READ | FILE_TXT | FILE_ANSI);
    
    if(file_handle != INVALID_HANDLE) {         
        // tạo mảng để ghi vào lines
        string lines[];
        while(!FileIsEnding(file_handle)) {
            string line = FileReadString(file_handle);   
            if(StringLen(line) > 0) {
                int size = ArraySize(lines);
                ArrayResize(lines, size + 1);
                lines[size] = line;
            }
        }
        FileClose(file_handle);
        
        if(lines.Size() > 1) {
            for(int i = 0; i < lines.Size(); i++) {
               //--- clear, dổi symbol, và frame
               if(StringFind(lines[i], "clear") != -1) {
                  DeleteAllObjects();
                  string data[];
                  ushort u_sep=StringGetCharacter("-",0);
                  StringSplit("" + lines[i], u_sep, data);
                  long chart_id = ChartID();
                  ENUM_TIMEFRAMES time_frame = PERIOD_M15;
                  if(data[1] == "m5") {
                     time_frame = PERIOD_M5;
                  }
                  ChartSetSymbolPeriod(chart_id, Symbol(), time_frame); 
                  Sleep(1000);              
               }
               
               //--- change, dổi frame
               if(StringFind(lines[i], "change") != -1) {
                  string data[];
                  ushort u_sep=StringGetCharacter("-",0);
                  StringSplit("" + lines[i], u_sep, data);
                  long chart_id = ChartID();
                  ENUM_TIMEFRAMES time_frame = PERIOD_M15;
                  if(data[1] == "m5") {
                     time_frame = PERIOD_M5;
                  }
                  ChartSetSymbolPeriod(chart_id, Symbol(), time_frame);
                  Sleep(1000);             
               }
               
               
               //--- draw kháng cự
               if(StringFind(lines[i], "resistance") != -1) {
                  string data[];
                  ushort u_sep=StringGetCharacter("-",0);
                  StringSplit("" + lines[i], u_sep, data);
                  long chart_id = ChartID();
                  double price1 = StringToDouble(data[1]);
                  double price2 = StringToDouble(data[2]);
                  datetime timestamp1 = StringToInteger(data[3]);
                  datetime timestamp2 = StringToInteger(data[4]);
                  string name = data[0] + "-" + data[1] + "-" +data[2] + "-" +data[3] + "-" +data[4] + "-" +data[5] + "-" + data[6];
                  DrawRectangle(chart_id, name, timestamp1 + PeriodSeconds(PERIOD_M15) * 10, price1, timestamp2 + PeriodSeconds(PERIOD_M15) * 10, price2, clrTomato, StringToColor(data[7]));
                  DrawText(chart_id, "text-" + name, data[ArraySize(data) - 1], timestamp2 + PeriodSeconds(PERIOD_M15), price1 > price2 ? price1: price2, clrRed, 40);
               }
               
               
               //--- draw hỗ trợ
               if(StringFind(lines[i], "support") != -1) {
                  string data[];
                  ushort u_sep=StringGetCharacter("-",0);
                  StringSplit("" + lines[i], u_sep, data);
                  long chart_id = ChartID();
                  double price1 = StringToDouble(data[1]);
                  double price2 = StringToDouble(data[2]);
                  datetime timestamp1 = StringToInteger(data[3]);
                  datetime timestamp2 = StringToInteger(data[4]);
                  DrawRectangle(chart_id,  data[0] + "-" + data[1] + "-" +data[2] + "-" +data[3] + "-" +data[4] + "-" +data[5] + "-" + data[6], timestamp1 + PeriodSeconds(PERIOD_M15) * 10, price1, timestamp2 + PeriodSeconds(PERIOD_M15) * 10, price2, clrLimeGreen, StringToColor(data[7]));
               }
               
               //--- draw trendline
               if(StringFind(lines[i], "trendline") != -1) {
                  string data[];
                  ushort u_sep=StringGetCharacter("-",0);
                  StringSplit("" + lines[i], u_sep, data);
                  long chart_id = ChartID();
                  double price1 = StringToDouble(data[1]);
                  double price2 = StringToDouble(data[2]);
                  datetime timestamp1 = StringToInteger(data[3]);
                  datetime timestamp2 = StringToInteger(data[4]);
                  DrawTrendline(chart_id,  data[0] + "-" + data[1] + "-" +data[2] + "-" +data[3] + "-" +data[4], timestamp1, price1, timestamp2, price2);
               }
               
               //--- draw future
               if(StringFind(lines[i], "future") != -1) {
                  string data[];
                  ushort u_sep=StringGetCharacter("-",0);
                  StringSplit("" + lines[i], u_sep, data);
                  long chart_id = ChartID();
                  datetime timestamp = StringToInteger(data[1]);
                  for(int i = 0; i < ArraySize(data); i++)
                  {
                     if(!(i == 0 || i == 1 || i == ArraySize(data) - 1)) {
                        double price1 = StringToDouble(data[i]);
                        double price2 = StringToDouble(data[i + 1]);
                        if(i + 1 == ArraySize(data) - 1) {
                           DrawTrendlineArrow(chart_id,  data[0] + "-" + timestamp + data[i], timestamp, price1, timestamp + (PeriodSeconds(PERIOD_M15) * 3), price2);
                        } else {
                           DrawTrendline(chart_id,  data[0] + "-" + timestamp + data[i], timestamp, price1, timestamp + (PeriodSeconds(PERIOD_M15) * 3), price2);
                        }
                        
                        timestamp += (PeriodSeconds(PERIOD_M15) * 3);
                     }
                  } 
               }


               //--- draw fibonacci
               if(StringFind(lines[i], "fibonacci") != -1) {
                  string data[];
                  ushort u_sep=StringGetCharacter("-",0);
                  StringSplit("" + lines[i], u_sep, data);
                  long chart_id = ChartID();
                  double price1 = StringToDouble(data[1]);
                  double price2 = StringToDouble(data[2]);
                  datetime timestamp1 = StringToInteger(data[3]);
                  datetime timestamp2 = StringToInteger(data[4]);
                  DrawFibonacci(chart_id,  data[0] + "-" + data[1] + "-" +data[2] + "-" +data[3] + "-" +data[4], timestamp1, price1, timestamp2, price2);
               }
               
               //--- draw proof
               if(StringFind(lines[i], "proof2") != -1 || StringFind(lines[i], "proof1") != -1) {

                  string data[];
                  ushort u_sep=StringGetCharacter("-",0);
                  StringSplit("" + lines[i], u_sep, data);
                  long chart_id = ChartID();
                  double price1 = StringToDouble(data[1]);
                  double price2 = StringToDouble(data[2]);
                  datetime timestamp1 = StringToInteger(data[3]);
                  datetime timestamp2 = StringToInteger(data[4]);
                  string name = data[0] + "-" + data[1] + "-" +data[2] + "-" +data[3] + "-" +data[4];
                  if(StringFind(lines[i], "cancel") != -1) {
                     ObjectDelete(chart_id, name);
                     ObjectDelete(chart_id, "line-" + name);
                  } else {
                     DrawRectangle(chart_id,  name, timestamp1 - PeriodSeconds(), price1, timestamp2 + PeriodSeconds(), price2, clrRed, C'255,250,190');
                  }
               }
                            
               //--- chụp hình
               if(StringFind(lines[i], "snapshort") != -1) {
                  Sleep(1000);
                  long chart_id = ChartID();
                  string data[];
                  ushort u_sep=StringGetCharacter("-",0);
                  StringSplit("" + lines[i], u_sep, data);
                  ChartScreenShot(chart_id, data[1], 1920, 1080, ALIGN_RIGHT);
               }
            }
            
            //--- clear file txt
            ClearFile(file_name); 
        }
        
    }
    else
    {
        Print("Không mở được file ", file_name, ". Error: ", GetLastError());
    }
}

void OnDeinit(const int reason)
{
    EventKillTimer();
}

void WriteCandle(string name_file, ENUM_TIMEFRAMES time_frame,  int bars, datetime last_time) {
   MqlRates rates[];
   if (CopyRates(Symbol(), time_frame, 0, bars, rates) <= 0)
   {
      Print("Không thể lấy dữ liệu nến.");
      return;
   }

   // Chỉ thực hiện nếu có nến mới (tránh ghi đè liên tục)
   if (rates[0].time == last_time)
      return;

   // Tạo handle cho Bollinger Bands
   int bb_handle = iBands(Symbol(), time_frame, 20, 0, 2.0, PRICE_CLOSE);


   // Mảng chứa dữ liệu Bollinger Bands
   double bb_upper[], bb_middle[], bb_lower[];

   // Lấy dữ liệu cho 180 nến gần nhất
   if (CopyBuffer(bb_handle, 0, 0, bars, bb_upper) <= 0 ||
       CopyBuffer(bb_handle, 1, 0, bars, bb_middle) <= 0 ||
       CopyBuffer(bb_handle, 2, 0, bars, bb_lower) <= 0)
   {
      Print("Không thể lấy dữ liệu Bollinger Bands.");
      return;
   }

   // Ghi file (tạo nếu chưa có, ghi đè nếu đã có)
   int file_handle = FileOpen(name_file, FILE_WRITE | FILE_TXT);
   if (file_handle == INVALID_HANDLE)
   {
      Print("Không thể mở tệp để ghi.");
      return;
   }

   // Ghi từng dòng dữ liệu từ nến cũ → mới
   for (int i = 0; i < bars; i++)
   {
      long timestamp = (long)rates[i].time;
      string line = StringFormat("%lld-%.5f-%.5f-%.5f-%.5f-%.5f-%.5f-%.5f",
                                 timestamp,
                                 rates[i].open,
                                 rates[i].close,
                                 rates[i].high,
                                 rates[i].low,
                                 bb_upper[i],
                                 bb_middle[i],
                                 bb_lower[i]);
      FileWrite(file_handle, line);
   }

   FileClose(file_handle);
   last_time = rates[0].time;
}

void ClearFile(const string file_name)
{
   int handle = FileOpen(file_name, FILE_WRITE | FILE_TXT);
   if(handle != INVALID_HANDLE)
   {
      FileWrite(handle, "drawdone");
      FileClose(handle);
      Print("Đã xóa dữ liệu trong file: ", file_name);
   }
   else
   {
      Print("Không thể mở file để xóa: ", file_name, ". Lỗi: ", GetLastError());
   }
}

void DrawRectangle( 
   long chart_id,
   string name,
   datetime time1,
   double price1,
   datetime time2,
   double price2,
   color rectangleColor,
   color fillColor,
   bool back = true
   ) {
   string border_name = "line-" + name;
   ObjectDelete(chart_id, name);
   ObjectDelete(chart_id, border_name);
   if(ObjectCreate(chart_id, name, OBJ_RECTANGLE, 0, time1, price1, time2, price2)) {
      ObjectSetInteger(chart_id, name, OBJPROP_STYLE, STYLE_SOLID);
      ObjectSetInteger(chart_id, name, OBJPROP_COLOR, fillColor);  // Viền
      ObjectSetInteger(chart_id, name, OBJPROP_FILL, fillColor); // Không trong suốt
      ObjectSetInteger(chart_id, name, OBJPROP_BORDER_TYPE, BORDER_FLAT);
      ObjectSetInteger(chart_id, name, OBJPROP_BORDER_COLOR, fillColor);
      ObjectSetInteger(chart_id, name, OBJPROP_BACK, back);
   } else {
      Print("Không thể tạo đối tượng hình chữ nhật ", name);
   }
   
   if(ObjectCreate(chart_id, border_name, OBJ_RECTANGLE, 0, time1, price1, time2, price2)) {
      ObjectSetInteger(chart_id, border_name, OBJPROP_COLOR, rectangleColor);
      ObjectSetInteger(chart_id,border_name,OBJPROP_WIDTH,1); 
      ObjectSetInteger(chart_id, border_name, OBJPROP_BACK, true);
   } else {
      Print("Không thể tạo đối tượng hình chữ nhật ", name);
   }
}

void DrawRectangleSimple( 
   long chart_id,
   string name,
   datetime time1,
   double price1,
   datetime time2,
   double price2,
   color rectangleColor
   ) {   
   ObjectDelete(chart_id, name);
   if(ObjectCreate(chart_id, name, OBJ_RECTANGLE, 0, time1, price1, time2, price2)) {
      ObjectSetInteger(chart_id, name, OBJPROP_COLOR, rectangleColor);
      ObjectSetInteger(chart_id,name,OBJPROP_WIDTH,2); 
      ObjectSetInteger(chart_id, name, OBJPROP_BACK, true);
   } else {
      Print("Không thể tạo đối tượng hình chữ nhật ", name);
   }
}


void DrawTrendline(long chart_id, string name, datetime time1, double price1, datetime time2, double price2, color clr = clrTomato)
{
   ObjectDelete(chart_id,name);
   if(ObjectCreate(chart_id, name, OBJ_TREND, 0, time1, price1, time2, price2))
   {
      ObjectSetInteger(chart_id, name, OBJPROP_COLOR, clr);
      ObjectSetInteger(chart_id, name, OBJPROP_WIDTH, 2); // độ dày
      ObjectSetInteger(chart_id, name, OBJPROP_RAY_RIGHT, false); // không kéo dài về bên phải
      ObjectSetInteger(chart_id, name, OBJPROP_RAY_LEFT, false); // không kéo dài về bên trái
      ObjectSetInteger(chart_id, name, OBJPROP_SELECTABLE, true); // có thể chọn
   }
}

void DrawTrendlineArrow(long chart_id, string name, datetime time1, double price1, datetime time2, double price2, color clr = clrTomato)
{
   ObjectDelete(chart_id,name);
   if(ObjectCreate(chart_id, name, OBJ_ARROWED_LINE, 0, time1, price1, time2, price2))
   {
      ObjectSetInteger(chart_id, name, OBJPROP_COLOR, clr);
      ObjectSetInteger(chart_id, name, OBJPROP_WIDTH, 2); // độ dày
      ObjectSetInteger(chart_id, name, OBJPROP_RAY_RIGHT, false); // không kéo dài về bên phải
      ObjectSetInteger(chart_id, name, OBJPROP_RAY_LEFT, false); // không kéo dài về bên trái
      ObjectSetInteger(chart_id, name, OBJPROP_SELECTABLE, true); // có thể chọn
   }
}


void DrawFibonacci(long chart_id, string name, datetime time1, double price1, datetime time2, double price2)
{
   ObjectDelete(chart_id, name); // Xoá Fibonacci chính
   ObjectsDeleteAll(chart_id, name + "_bg_", 0); // Xoá các vùng nền cũ nếu có

   double levels[] = {0.0, 0.236, 0.382, 0.5, 0.618, 0.786, 1.0, 1.618, 2.618, 3.618, 4.236};
   color colors[] = {
      C'128,128,128',  // 0.0
      C'242,54,69',    // 0.236
      C'255,152,0',    // 0.382
      C'76,178,80',    // 0.5
      C'8,153,129',    // 0.618
      C'0,188,212',    // 0.786
      C'128,128,128',  // 1.0
      C'41,98,255',    // 1.618
      C'242,54,69',    // 2.618
      C'156,39,176',   // 3.618
      C'233,30,99'     // 4.236
   };
   
   color bgs[] = {
      C'255,245,246',  // 0.0 - hồng rất nhạt
      C'255,250,240',  // 0.236 - cam rất nhạt
      C'245,255,245',  // 0.382 - xanh lá rất nhạt
      C'240,250,250',  // 0.5 - xanh dương rất nhạt
      C'240,255,255',  // 0.618 - xanh lam rất nhạt
      C'250,250,250',  // 0.786 - xám rất nhạt
      C'240,245,255',  // 1.0 - xanh tím rất nhạt
      C'255,240,242',  // 1.618 - hồng rất nhạt
      C'250,240,252',  // 2.618 - tím rất nhạt
      C'255,235,245',  // 3.618 - hồng đậm rất nhạt
      C'255,235,245'   // 4.236 - giống 3.618
   };

   if (ObjectCreate(chart_id, name, OBJ_FIBO, 0, time1, price1, time2, price2))
   {
      ObjectSetInteger(chart_id, name, OBJPROP_RAY_RIGHT, true);
      ObjectSetInteger(chart_id, name, OBJPROP_WIDTH, 1);
      ObjectSetInteger(chart_id, name, OBJPROP_STYLE, STYLE_DASH);
      ObjectSetInteger(chart_id, name, OBJPROP_COLOR, C'128,128,128');

      ObjectSetInteger(chart_id, name, OBJPROP_LEVELS, ArraySize(levels));

      for (int i = 0; i < ArraySize(levels); i++)
      {
         ObjectSetDouble(chart_id, name, OBJPROP_LEVELVALUE, i, levels[i]);
         ObjectSetInteger(chart_id, name, OBJPROP_LEVELCOLOR, i, colors[i]);
         ObjectSetInteger(chart_id, name, OBJPROP_LEVELWIDTH, i, 1.5);
         ObjectSetInteger(chart_id, name, OBJPROP_LEVELSTYLE, i, STYLE_SOLID);
         ObjectSetString(chart_id, name, OBJPROP_LEVELTEXT, i, DoubleToString(levels[i] * 100, 1) + "%");
      }
   }

   // Vẽ nền giữa các levels (chỉ trong vùng [0.0, 1.0])
   double top = price1, bottom = price2;
   if (price2 > price1) {
      top = price2;
      bottom = price1;
   }

   double height = top - bottom;

   for (int i = 0; i < ArraySize(levels) - 1; i++)
   {
      double level1 = top - levels[i] * height;
      double level2 = top - levels[i + 1] * height;

      string rect_name = name + "_bg_" + IntegerToString(i);
      datetime time_start = time1;
      if(time2 < time1) {
         time_start = time2;
      }
      if (ObjectCreate(chart_id, rect_name, OBJ_RECTANGLE, 0, time_start, level1, time2 + PeriodSeconds() * 100, level2))
      {
         ObjectSetInteger(chart_id, rect_name, OBJPROP_COLOR, bgs[i]);
         ObjectSetInteger(chart_id, rect_name, OBJPROP_STYLE, STYLE_SOLID);
         ObjectSetInteger(chart_id, rect_name, OBJPROP_WIDTH, 1);
         ObjectSetInteger(chart_id, rect_name, OBJPROP_BACK, true);
         ObjectSetInteger(chart_id, rect_name, OBJPROP_FILL, true);
      }
   }
}

void DrawText(long chart_id, string name, string text, datetime time, double price, color clr = clrRed, int fontSize = 12, string fontName = "Arial", ENUM_ANCHOR_POINT anchor = ANCHOR_LEFT_UPPER)
{
   ObjectDelete(chart_id, name);
   int x = 0;
   int y = 0;
   if(ChartTimePriceToXY(ChartID(), 0, time, price, x, y)) {
   
   }


   if (ObjectCreate(chart_id, name, OBJ_LABEL, 0, 0, 0))
   {
      ObjectSetInteger(0, name, OBJPROP_CORNER, CORNER_LEFT_UPPER);
      ObjectSetInteger(0, name, OBJPROP_XDISTANCE, x);
      ObjectSetInteger(0, name, OBJPROP_YDISTANCE, y);
      ObjectSetInteger(0, name, OBJPROP_FONTSIZE, fontSize);
      ObjectSetInteger(0, name, OBJPROP_COLOR, clr);
      ObjectSetInteger(0, name, OBJPROP_ANCHOR, anchor);
      ObjectSetString(0, name, OBJPROP_TEXT, text);
      ObjectSetString(0, name, OBJPROP_FONT, fontName);
   }


}


void DeleteAllObjects()
{
   int total = ObjectsTotal(0);
   for(int i = total - 1; i >= 0; i--)
   {
      string name = ObjectName(0, i);
      ObjectDelete(0, name);
   }
}

string GenerateRandomName(int length = 40)
{
   string chars = "abcdefghijklmnopqrstuvwxyz0123456789";
   string result = "rect_";  // prefix để dễ phân loại, chiếm 5 ký tự
   int total = StringLen(chars);
   MathSrand((uint)TimeLocal()); // khởi tạo seed theo thời gian hiện tại

   for(int i = 0; i < length - StringLen(result); i++)
   {
      int index = MathRand() % total;
      result += StringSubstr(chars, index, 1);
   }

   return result;
}