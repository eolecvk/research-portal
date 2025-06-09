import sys
import logging
from query_engine import generate_ai_response # Import the centralized function

# Configure basic logging for CLI
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def print_headers():
    # ... (unchanged ASCII art) ...
    logo = r'''
                                 =/;;/-
                                 +:     //
                                 /;       /;
                                 -X         H.
         .//;;;:;;-,   X=         :+   .-;:=;:;%;.
         M-         ,=;;;#:,     ,:#;;:=,         @
         :%           :%.=/++++/=.$=         %=
         ,%;          %/:+/;,,/++:+/         ;+.
         ,+/.    ,;@+,         ,%H;,    ,/+,
                 ;+;;/= @. .H##X   -X :///+;
                 ;+=;;;.@, .XM@$. =X.//;=%/.
         ,;:      :@%=         =$H:     .+%-
         ,%=          %;-///==///-//         =%,
         ;+           :%-;;;;;;;;-X-         +:
         @-      .-;;;;M-         =M/;;;-.     -X
         :;;::;;-.    %-         :+   ,-;;-;:==
                                 ,X         H.
                                 ;/       %=
                                 //   +;
                                 ,////,

'''

    title = r'''
____                                 _      ____          _      _
| _ \ ___  ___  ___  __ _ _ __ ___| |__   | _ \ ___  _ __| |_ __ _| |
| |_) / _ \/ __|/ _ \/ _` | '__/ __| '_ \  | |_) / _ \| '__| __/ _` | |
| _ <  __/\__ \ __/ (_| | | | (__| | | | | __/ (_) | |  | || (_| | |
|_| \_\___||___/\___|\__,_|_|  \___|_| |_| |_|  \___/|_|   \__\__,_|_|
'''
    print(logo)
    print(title)

def main():
    print_headers()

    while True:
        query = input("\nWhat do you need?\n > ")
        if query.lower() in ['exit', 'quit']:
            logger.info("Exiting CLI.")
            break
        try:
            logger.info("Thinking...")
            # Call the centralized AI response generation function
            response_text = generate_ai_response(query)
            print(response_text)
        except ValueError as ve:
            logger.error(f"Configuration Error: {ve}")
            print(f"Error: {ve}. Please check your environment setup.")
        except Exception as e:
            logger.error(f"An unexpected error occurred during the request: {e}", exc_info=True)
            print(f"An error occurred: {e}. Please try again.")
        sys.stdout.flush() # Ensure output is immediately visible

if __name__ == "__main__":
    main()