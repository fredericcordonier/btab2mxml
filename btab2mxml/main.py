from argparse import  ArgumentParser
from pathlib import Path
import logging
import traceback
from btab2mxml.btab.btab_reader import BtabReader, BtabReaderBadReadModeException
from btab2mxml.btab.btab_tokenizer import BtabTokenizer, EndToken
from btab2mxml.btab.btab_parser import BtabParser


def normalize_suffix(s):
    return s if s.startswith('.') else '.' + s

def parse_args():
    parser = ArgumentParser(description="Supported arguments")
    parser.add_argument("--infile", type=Path, nargs='+', help='Input file name')
    parser.add_argument("--indir", type=Path, nargs='?', help='Input directory')
    parser.add_argument("--outdir", type=Path, default=Path("out"), help="Output directory (default: ./out)")
    parser.add_argument("--suffix", default='btab', type=normalize_suffix, help='Extension for tablature files')
    parser.add_argument("--overwrite", action='store_true', help="Force overwrite of existing .xml files")
    parser.add_argument("--verbose", action='store_true', help="Display exception details")
    return parser.parse_args()


def setup_logging(verbose: bool, logfile='app.log'):
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

     # Handler fichier (tout)
    fh = logging.FileHandler(logfile, mode='w', encoding='utf-8')
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)

    # Handler console (filtré)
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG if verbose else logging.INFO)
    ch.setFormatter(formatter)
    logger.addHandler(ch)

def get_file_stems(path: Path, suffix: str):
    return [f.stem for f in path.iterdir() if f.suffix == suffix and f.is_file()]

def main():
    args = parse_args()
    args.outdir.mkdir(parents=True, exist_ok=True)
    setup_logging(args.verbose)

    tab_stems = set()
    xml_stems = set()

    if args.infile:
        # Handling individual file names
        existing = [f for f in args.infile if f.exists() and f.suffix == args.suffix]
        tab_stems.update(f.stem for f in existing)

    if args.indir:
        # Handling input dir
        if not args.indir.is_dir():
            logging.error("Please specify an existing input directory.")
            return
        tab_stems.update(get_file_stems(args.indir, args.suffix))
        xml_stems.update(get_file_stems(args.outdir, '.xml'))

    to_process = sorted(tab_stems) if args.overwrite else sorted(tab_stems - xml_stems)

    for stem in to_process:
        # Check if stem was in infile or indir to retrieve its path
        in_file = next((f for f in (args.infile or []) if f.stem == stem), None)
        if not in_file and args.indir:
            in_file = args.indir / f"{stem}{args.suffix}"
        out_file = args.outdir / f"{stem}.xml"

        logging.info(f"Conversion : {in_file} -> {out_file}")
        reader = BtabReader(in_file)
        tokenizer = BtabTokenizer(reader)
        parser = BtabParser(tokenizer)
        try:
            parser.parse()
        except Exception as e:
            logging.error(f"Exception occurred for file {in_file}, {e}")
            if args.verbose:
                logging.debug(traceback.format_exc())
            continue
        else:
            parser.output(out_file)

if __name__ == "__main__":
    main()
