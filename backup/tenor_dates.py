from datetime import timedelta
from datetime import datetime
from dateutil.relativedelta import relativedelta
import holidays
import pandas as pd
import numpy as np
from miscellaneous import InputError
from typing import Union


class TenorDates:

    standard_tenors = ["ON", "1W", "2W", "1M", "2M", "3M", "6M", "9M", "1Y", "2Y", "5Y", "10Y"]
    supported_ccy = ["USD", "GBP", "EUR", "JPY", "CHF", "AUD", "CAD", "NZD", "SEK", "NOK"]
    ccy_country_code = {
        "USD": ["United States", "US"], 
        "GBP": ["United Kingdom", "GB"], 
        "EUR": ["Europe", "ECB"],
        "JPY": ["Japan", "JP"], 
        "CHF": ["Switzerland", "CH"], 
        "AUD": ["Australia", "AU"], 
        "CAD": ["Canada", "CA"],
        "NZD": ["New Zealand", "NZ"],
        "SEK": ["Sweden", "SE"],
        "NOK": ["Norway", "NO"]  
    }

    """
    Four important dates for market tenor calculations in FX Options Market
    ---Horizon---Spot Date-----------------------------Expiry---Delivery---
    - Horizon: trade date
    - Spot date (settlement)
    - Expiry date: 
    - 
    """

    def __init__(self, ccy: str) -> None:
        assert type(ccy) == str, "ccy input must be string!"
        assert (len(ccy) == 6) and (ccy[0:3] in self.supported_ccy) and ((ccy[3:6] in self.supported_ccy)),\
                f"ccy input must be in the form of 'CCY1CCY2'! Supported currencies: {self.supported_ccy}"
        self.ccy = ccy

    def is_business_day(self, date:datetime) -> bool:
        """Check if a date is a business day. 
        A date is counted as a business day when it is 
        not a weekday & not a holiday in both
        countries (even if it is a US holiday).

        Args:
            date (datetime): date

        Returns:
            bool: True if the date is a business day
        """
        assert type(date) == datetime, "date must be of type 'datetime'!"
        # Get non-US holidays only
        if "USD" in self.ccy:
            ccy = self.ccy.replace("USD", "")
            ccy_holidays = holidays.country_holidays(self.ccy_country_code[ccy][1])
            return bool(len(pd.bdate_range(date, date))) and date not in ccy_holidays
        else:
            # Get both currencies' holidays 
            ccy1 = self.ccy[0:3]
            ccy1_holidays = holidays.country_holidays(self.ccy_country_code[ccy1][1])
            ccy2 = self.ccy[3:6]
            ccy2_holidays = holidays.country_holidays(self.ccy_country_code[ccy2][1])
            return bool(len(pd.bdate_range(date, date))) and (date not in ccy1_holidays) and (date not in ccy2_holidays)
            
    def is_valid_spot(self, date: datetime) -> bool:
        """Check if a date is a valid spot
        - must be a business day in the US
        - muust be a business day in both currencies

        Args:
            date (datetime): date

        Returns:
            bool: True if the date is a valid spot date
        """
        # Spot (settlement or delivery) date is two business days after horizon / expiry
        # - must be a business day in US
        # - must be a business day in both currencies
        us_holidays = holidays.country_holidays(self.ccy_country_code["USD"][1])

        return self.is_business_day(date = date) and (date not in us_holidays)

    def is_valid_expiry(self, date:datetime) -> bool:
        """Check if a date is a valid expiry

        Args:
            date (datetime): date

        Returns:
            bool: True if the date is a valid expiry date
        """
        assert type(date) == datetime, "date must be of type 'datetime'!"
        # Expiry date can be any weekday when 
        # - at least one marketplace is open 
        # - not 1st January
        ccy1 = self.ccy[0:3]
        ccy1_holidays = holidays.country_holidays(self.ccy_country_code[ccy1][1])
        ccy2 = self.ccy[3:6]
        ccy2_holidays = holidays.country_holidays(self.ccy_country_code[ccy2][1])

        return bool(len(pd.bdate_range(date, date))) and not ((date.day == 1) and (date.month == 1)) \
            and ((date not in ccy1_holidays) or (date not in ccy2_holidays))

    def next_business_day(self, date:datetime) -> bool:
        """Returns the next business day

        Args:
            date (datetime): date

        Returns:
            datetime: next business day
        """

        assert type(date) == datetime, "datetime object must be passed to argument date!"
    
        date += timedelta(days = 1)
        if self.is_business_day(date = date): 
            return date
        else:
            return self.next_business_day(date = date)
    
    def prev_business_day(self, date:datetime) -> bool:
        """Returns the previous business day

        Args:
            date (datetime): date

        Returns:
            datetime: next business day
        """

        assert type(date) == datetime, "datetime object must be passed to argument date!"
    
        date -= timedelta(days = 1)
        if self.is_business_day(date = date): 
            return date
        else:
            return self.prev_business_day(date = date)

    def next_valid_spot(self, date: datetime) -> datetime:
        """Returns the next valid spot date

        Args:
            date (datetime): date

        Returns:
            datetime: next valid spot date
        """

        assert type(date) == datetime, "datetime object must be passed to argument date!"
    
        date += timedelta(days = 1)
        if self.is_valid_spot(date = date): 
            return date
        else:
            return self.next_valid_spot(date = date)
    
    def prev_valid_spot(self, date: datetime) -> datetime:
        """Returns the previous valid spot date

        Args:
            date (datetime): date

        Returns:
            datetime: next valid spot date
        """

        assert type(date) == datetime, "datetime object must be passed to argument date!"
    
        date -= timedelta(days = 1)
        if self.is_valid_spot(date = date): 
            return date
        else:
            return self.prev_valid_spot(date = date)
    
    def next_valid_expiry(self, date: datetime) -> datetime:
        """Returns the next valid expiry date

        Args:
            date (datetime): date

        Returns:
            datetime: next valid expiry date
        """

        assert type(date) == datetime, "datetime object must be passed to argument date!"
    
        date += timedelta(days = 1)
        if self.is_valid_expiry(date):
            return date
        else:
            return self.next_valid_expiry(date = date)

    def prev_valid_expiry(self, date: datetime) -> datetime:
        """Returns the previous valid expiry date

        Args:
            date (datetime): date

        Returns:
            datetime: next valid expiry date
        """

        assert type(date) == datetime, "datetime object must be passed to argument date!"
    
        date -= timedelta(days = 1)
        if self.is_valid_expiry(date):
            return date
        else:
            return self.prev_valid_expiry(date = date)

    def spot_from_horizon(self, horizon_date: datetime) -> datetime:
        """Returns spot date from a horizon date 

        Args:
            horizon_date (datetime): horizon date.

        Returns:
            datetime: spot date
        """
        assert self.is_business_day(horizon_date), "Horizon date is not a business day!"

        if self.ccy in ["USDCAD", "USDTRY", "USDPHP", "USDRUB"]:
            # T + 1 business day from horizon date
            return self.next_valid_spot(date = horizon_date)
        else:
            # T + 2 business days from horizon date
            next_business_day = self.next_business_day(date = horizon_date)
            return self.next_valid_spot(date = next_business_day)

    def horizon_from_spot(self, spot_date: datetime) -> datetime:
        """Returns horizon date from a spot date 

        Args:
            spot_date (datetime): spot date.

        Returns:
            datetime: horizon date.
        """
        assert self.is_valid_spot(spot_date), "Spot date is not valid!"
        
        if self.ccy in ["USDCAD", "USDTRY", "USDPHP", "USDRUB"]:
            # T - 1 business day from spot date
            return self.prev_valid_expiry(date = spot_date)
        else:
            # T - 2 business days from spot date
            prev_business_day = self.prev_business_day(date = spot_date)
            return self.prev_valid_expiry(date = prev_business_day)

    def expiry_from_tenor(self, horizon_date: datetime, tenor: str) -> datetime:
        """Returns expiry date from a horizon date given market tenor

        Args:
            horizon_date (datetime): horizon date.
            tenor (str): market tenor eg. "ON", "2W", "6M", "5Y"

        Returns:
            datetime: expiry date
        """

        if tenor == "ON":
            return self.next_valid_expiry(date = horizon_date)
        elif tenor[-1] == "D":
            expiry = horizon_date + timedelta(days = int(tenor[:-1]))
            if self.is_valid_expiry(date = expiry):
                return expiry
            else:
                return self.next_valid_expiry(date = expiry)
        elif tenor[-1] == "W":
            expiry = horizon_date + timedelta(days = int(tenor[:-1]) * 7)
            if self.is_valid_expiry(date = expiry):
                return expiry
            else:
                return self.next_valid_expiry(date = expiry)
        elif (tenor[-1] == "M") or (tenor[-1] == "Y"):
            # Calculate no. of months to move forward
            if (tenor[-1] == "M"):
                n_months = int(tenor[:-1])
            elif (tenor[-1] == "Y"):
                n_months = int(int(tenor[:-1])*12)
            # first calculate the spot date
            spot_date = self.spot_from_horizon(horizon_date = horizon_date)
            # then calculate delivery date
            delivery_date = spot_date + relativedelta(months = n_months)
            if not self.is_valid_spot(date = delivery_date):
                delivery_date = self.next_valid_spot(date = delivery_date)
            # If delivery date falls in the month after n months, then 
            # shifts the date backward until a valid delivery date is 
            # found
            while ((delivery_date.month - spot_date.month) > n_months):
                delivery_date = self.prev_valid_spot(date = delivery_date)
            # calculate expiry date the same way the horizon date is calculated 
            # from the spot date
            expiry = self.horizon_from_spot(spot_date = delivery_date)
            if self.is_valid_expiry(date = expiry):
                return expiry
            else:
                return self.prev_valid_expiry(date = expiry)
        else:
            raise InputError("Invalid input, must be in the form: 'ON', '5W', '7M', '1Y' etc...")

    def populate_expiry_dates(self, horizon_date: datetime, return_df = False) -> Union[dict, pd.DataFrame]:
        """Returns expiry dates of standard market tenor given horizon date.

        Args:
            horizon_date (datetime): horizon date.
            return_df (bool, optional): return dataframe if True. Defaults to False.

        Returns:
            Union[dict, pd.DataFrame]: expiry dates from standard tenors
        """
        expiry_dates = {}
        expiry_dates["Horizon"] = [horizon_date.strftime("%a %d-%b-%Y")]
        expiry_dates["Tenor"] = self.standard_tenors
        expiry_dates["Expiry Date"] = [self.expiry_from_tenor(horizon_date = horizon_date, tenor = tenor).strftime("%a %d-%b-%Y") 
                                        for tenor in self.standard_tenors]
        if return_df:
            return pd.DataFrame.from_dict(expiry_dates, orient = "index").transpose()
        return expiry_dates

    def bdate_range(self, start_date: datetime, end_date: datetime) -> list:
        """Returns a list of business days between two dates (inclusive)

        Args:
            date1 (datetime): start date
            date2 (datetime): end date

        Returns:
            list: business days between dates (inclusive)
        """
        b_dates = pd.bdate_range(start_date, end_date).to_pydatetime()

        return [fx_b_date for fx_b_date in b_dates if self.is_business_day(date = fx_b_date)]
            


# tenor = TenorDates(ccy = "EURUSD")
# date = datetime.strptime('11-06-2014', '%d-%m-%Y')
# print(tenor.populate_expiry_dates(horizon_date = date, return_df=True))
# expiry = tenor.expiry_from_tenor(horizon_date = date, tenor = "1M")
# settlement = tenor.spot_from_horizon(horizon_date = date)
# print("Expiry = ", expiry.strftime('%a %d-%m-%Y'))
# print("Settlement = ", settlement.strftime('%a %d-%m-%Y'))
# print(tenor.bdate_range(start_date = datetime.strptime('11-06-2014', '%d-%m-%Y'), end_date= datetime.strptime('11-12-2014', '%d-%m-%Y')))

