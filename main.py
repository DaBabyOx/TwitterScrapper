import asyncio
from auth import getClient
from search import search, csvSave, jsonSave, xlsxSave

async def main():
    client = getClient()
    help_text = (
        '''
        Advanced Search Examples:
        gold price                      → basic keyword search
        "gold price"                    → exact phrase
        from:elonmusk                   → tweets from a user
        @binance                        → tweets mentioning a user
        #AI                             → hashtag search
        bitcoin since:2024-01-01        → tweets since a date
        gold until:2024-06-01           → tweets before a date
        (gold OR silver) lang:en        → multiple keywords, only English
        bitcoin -dogecoin               → include bitcoin, exclude dogecoin
        (gold OR bitcoin) since:2024-01-01 until:2024-02-01 lang:en → full advanced search
        '''
    )

    while True:
        q = input("Hi there!\nEnter your search query (or type '-help' or '-quit'): ").strip()

        if not q:
            print('Please enter a search query.\n')
            continue

        if q.lower() == '-quit':
            print('Goodbye!')
            return

        if q.lower() == '-help':
            print(help_text)
            continue

        break
    
    c = input('How many tweets to fetch (default is 10): ').strip()
    c = int(c) if c.isdigit() else 10
    
    pd = input('Which should I search? Top or Latest tweets? (default is Top): ').strip().capitalize()
    if pd not in ('Top', 'Latest'): pd = 'Top'
    
    tweets = await search(client, q, count = c, product = pd)
    
    while True:
        try:
            fi = input("Choose format(s):\n1. CSV (default)\n2. XLSX\n3. JSON\n>> ").strip()
            if fi == '':
                f = [1]
                break
            
            f = [int(x) for x in fi.split(',')]
            
            if all(i in (1, 2, 3) for i in f):
                break
            else:
                print('Please enter only 1, 2, or 3 (you can separate with commas, e.g. 1,3)')
        except ValueError:
            print('input integer(s) only!')
    
    for i in f:
        (csvSave if i == 1 else xlsxSave if i == 2 else jsonSave)(tweets, q)

if __name__ == '__main__':
    asyncio.run(main())