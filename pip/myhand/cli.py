from myhand.main import main

def cli(default="", run=False):
    main(default, run)

if __name__ == "__main__":
    import argparse
    # Create the parser
    parser = argparse.ArgumentParser(description="Process some inputs.")
    # Add arguments
    parser.add_argument("default", nargs="?", default=None, help="enter default entry")
    parser.add_argument('-r', '--run', action='store', dest='run', help="run default entry with -r flag")
    # Parse arguments
    args = parser.parse_args()
    # Check what kind of arguments were provided and perform actions accordingly
    if args.run:
        cli(args.run, True)
    elif args.default:
        cli(args.default)
    else:
        cli()
    
