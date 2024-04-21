"""
SynthTIGER
Copyright (c) 2021-present NAVER Corp.
MIT license
"""

import argparse
import pprint
import time

import synthtiger
from tqdm import tqdm
from pathlib import Path
import os
import sys

def run(args):
    if args.config is not None:
        config = synthtiger.read_config(args.config)

    pprint.pprint(config)

    synthtiger.set_global_random_seed(args.seed)
    template = synthtiger.read_template(args.script, args.name, config)
    generator = synthtiger.generator(
        args.script,
        args.name,
        config=config,
        count=args.count,
        worker=args.worker,
        seed=args.seed,
        retry=True,
        verbose=args.verbose,
        font_wise_separate_data=args.font_wise_separate_data,
        font_dir=args.font_dir,
    )

    if args.output is not None:
        template.init_save(args.output)

    for idx, (task_idx, data) in enumerate(tqdm(generator, total=args.count, desc="Generating data")):
        if args.output is not None:
            template.save(args.output, data, task_idx)
        # print(f"Generated {idx + 1} data (task {task_idx})")

    if args.output is not None:
        template.end_save(args.output)


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-o",
        "--output",
        metavar="DIR",
        type=str,
        help="Directory path to save data.",
    )
    parser.add_argument(
        "-c",
        "--count",
        metavar="NUM",
        type=int,
        default=100,
        help="Number of output data. [default: 100]",
    )
    parser.add_argument(
        "-w",
        "--worker",
        metavar="NUM",
        type=int,
        default=0,
        help="Number of workers. If 0, It generates data in the main process. [default: 0]",
    )
    parser.add_argument(
        "-s",
        "--seed",
        metavar="NUM",
        type=int,
        default=None,
        help="Random seed. [default: None]",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="Print error messages while generating data.",
    )
    parser.add_argument(
        "script",
        metavar="SCRIPT",
        type=str,
        help="Script file path.",
    )
    parser.add_argument(
        "name",
        metavar="NAME",
        type=str,
        help="Template class name.",
    )
    parser.add_argument(
        "config",
        metavar="CONFIG",
        type=str,
        nargs="?",
        help="Config file path.",
    )
    parser.add_argument(
        "-fsd",
        "--font_wise_separate_data",
        action="store_true",
        help="""
            if font_wise_separate_data set to True it will store data for each font
            else it will generate original format mix of data. Default to false.
        """,
        default=False,
    )
    parser.add_argument(
        "-fd",
        "--font_dir",
        type=str,
        nargs="?",
        help="Define a font directory to be used",
    )
    # args = parser.parse_args()

    # pprint.pprint(vars(args))

    # return args
    return parser.parse_args()



def main():
    start_time = time.time()
    args = parse_args()
    run(args)
    if args.font_wise_separate_data:
        # Create font (path) list
        if args.font_dir:
            fonts = [
                os.path.join(args.font_dir, p)
                for p in os.listdir(args.font_dir)
                if os.path.splitext(p)[1] == ".ttf"
            ]
        elif args.font:
            if os.path.isfile(args.font):
                fonts = [args.font]
            else:
                sys.exit("Cannot open font")
        else:
            fonts = load_fonts(args.language)

        # TODO -- replace print messages with loguru logger
        print(f"INFO : Total font files: {len(fonts)}")

        # KEEP ORIGINAL OUTPUT DIR
        original_output_dir = args.output_dir

        for font in fonts:
            font_stem = Path(font).stem
            print(f"=" * 50)
            print(f"Generating data for font : {font_stem}")
            args_dict = vars(args)

            # update font and output dir
            args_dict["font_dir"] = None
            args_dict["font"] = font
            args_dict["output_dir"] = os.path.join(original_output_dir, font_stem)
            os.makedirs(args_dict["output_dir"], exist_ok=True)

            # pass argparse argument to function as-kwargs
    #         generate_text_data(**args_dict)
    #         print("\n")
    # else:
    #     ## Default mode
    #     generate_text_data(**vars(args))


    end_time = time.time()
    print(f"{end_time - start_time:.2f} seconds elapsed")


if __name__ == "__main__":
    main()
