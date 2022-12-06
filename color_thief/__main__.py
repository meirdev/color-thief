import argparse

from rich.console import Console

from . import factory, rgb_to_hex


def main() -> None:
    arg_parser = argparse.ArgumentParser()
    arg_parser.add_argument("src", help="Path to image file")
    arg_parser.add_argument(
        "-c", "--count", type=int, default=10, help="Number of colors to return"
    )
    arg_parser.add_argument(
        "-a",
        "--algo",
        default="kmeans[RGB]",
        help="Algorithm to use",
        choices=["kmeans[RGB]", "kmeans[LAB]", "regular", "octree", "median_cut"],
    )
    arg_parser.add_argument("-o", "--output", help="Path to output file")

    args = arg_parser.parse_args()

    colors_counter = factory(args.src, args.algo, args.count)

    console = Console(highlighter=None, record=True)

    for color in colors_counter:
        color_repr = rgb_to_hex(color)

        console.print("■", style=color_repr, end=" ")
        console.print(color_repr)

    if args.output:
        console.save_svg(args.output, title="Color Thief")


if __name__ == "__main__":
    main()
