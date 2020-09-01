import re
from xml.dom import minidom

class Emoji:
    
    @classmethod
    def add_label_category(cls, categ):
        emoji = ''
        for lc in cls.LABEL_CATEGORY:
            if re.search(r'(?i)'+lc, categ):
                emoji = cls.LABEL_CATEGORY.get(lc)
        
        return "%s %s " % (emoji, categ ) 

    LABEL_CATEGORY ={
        # product_category_Food_Drinks
        'Groceries': '🥦🛒',
        'Bar, Cafe': '🍻☕',
        'Food & Drinks':'🍝🥤',
        'Restaurant, fast-food': '🍕',
        
        # product_category_Shopping
        'Shopping': '🛍️',
        'Clothes & shoes':'👟🧤', 
        'Drug-store, chemist':'💊', 
        'Electronics, accessories':'📱📷💻', 
        'Free time':'🎬', 
        'Gifts, joy':'🎁', 
        'Health and beauty':'🧼', 
        'Home, garden':'🏡', 
        'Jewels, accessories':'⌚💍💎', 
        'Kids':'🍼🧸🎈', 
        'Pets, animals':'🐶🐦🐟', 
        'Stationery, tools':'⚙️🗞️', 
        
        # product_category_Housing
        'Housing':'🏠',         
        'Energy, utilities':'🏠💡', 
        'Maintenance, repairs':'🏠🛠️', 
        'Mortgage':'🏠💵', 
        'Property insurance':'🏠🔐', 
        'Rent':'🏠💴', 
        'Services':'🔌💧🚰', 

        # product_category_Transportation
        'Transportation':'🚌',         
        'Business trips':'✈', 
        'Long distance':'🛬🚆', 
        'Public transport':'🚎', 
        'Taxi':'🚕',

        # product_category_Vehicle
        'Vehicle':'🚘',         
        'Fuel':'⛽', 
        'Leasing':'', 
        'Parking':'🚘🎟️', 
        'Rentals':'', 
        'Vehicle insurance':'🚘🔐', 
        'Vehicle maintenance':'🚘 ⚙️', 

        # product_category_Life_Entertainment
        'Life & Entertainment':'',         
        'Active sport, fitness':'💪', 
        'Alcohol, tobacco':'🚬🍻', 
        'Books, audio, subscriptions':'📚💽', 
        'Charity, gifts':'🤝💝', 
        'Culture, sport events':'🎭🎫', 
        'Education, development':'🎓', 
        'Health care, doctor':'👩‍⚕️', 
        'Hobbies':'🎨', 
        'Holiday, trips, hotels':'🏢', 
        'Life events':'🍾', 
        'Lottery, gambling':'', 
        'TV, Streaming':'📺', 
        'Wellness, beauty':'', 

        # product_category_Communication_PC
        'Communication, PC':'💻', 
        'Internet':'📶', 
        'Phone, mobile phone':'📱', 
        'Postal services':'📦', 
        'Software, apps, games':'👩‍💻', 

        # product_category_Financial_Expenses
        'Financial expenses':'🏦',         
        'Advisory':'🤵‍♂️', 
        'Charges, Fees':'', 
        'Child Support':'🚼', 
        'Fines':'', 
        'Insurances':'', 
        'Loan, interests':'💸', 
        'Taxes':'🏦', 

        # product_category_Investments
        'Investments':'📊',         
        'Collections':'', 
        'Financial investments':'📈', 
        'Realty':'🏫', 
        'Savings':'💰', 
        'Vehicles, chattels':'🚘', 

        # product_category_Income
        'Income':'💰',         
        'Checks, coupons':'🎫', 
        'Child Support':'🚼', 
        'Dues & grants':'', 
        'Gifts':'🎁', 
        'Interests, dividends':'💹', 
        'Lending, renting':'💸', 
        'Lottery, gambling':'', 
        'Refunds (tax, purchase)':'🏦', 
        'Rental income':'💰', 
        'Sale':'🏷️', 
        'Wage, invoices':'🧾', 
        # product_category_Others
        'Others':'', 
        

    }    