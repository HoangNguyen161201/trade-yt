#property copyright "Copyright 2024, MetaQuotes Ltd."
#property link      "https://www.mql5.com"
#property version   "1.00"

int OnInit()
  {
  
   // lấy ra id biểu đồ
   long chart_id= ChartID();
  
   // sử dụng đồng tiền
   ChartSetSymbolPeriod(chart_id, "XAUUSDm", PERIOD_H4);
   
   // sử dụng template
   ChartApplyTemplate(chart_id, "price-action.tpl");
   
   return(INIT_SUCCEEDED);
  }


void OnTick()
  {
//---
   
  }
