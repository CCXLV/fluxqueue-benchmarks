import random
import string
from pathlib import Path


def random_local_part(length: int = 10) -> str:
    chars = string.ascii_lowercase + string.digits
    return "".join(random.choice(chars) for _ in range(length))


def main(total: int) -> None:
    project_root = Path(__file__).resolve().parent.parent
    output_path = project_root / "scripts" / "emails.txt"

    domain = "example.com"

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", encoding="utf-8") as f:
        for i in range(1, total + 1):
            local = f"user{i}_{random_local_part(8)}"
            email = f"{local}@{domain}"
            f.write(email + "\n")

            if i % 100_000 == 0:
                print(f"Generated {i} emails into {output_path}")


if __name__ == "__main__":
    main(1_000_000)
