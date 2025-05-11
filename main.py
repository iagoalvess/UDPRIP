import sys

from udprip.core.router import Router


def main():
    if len(sys.argv) < 3:
        print("Uso: ./router.py <ip> <periodo> [arquivo_startup]")
        sys.exit(1)

    self_ip = sys.argv[1]
    update_period = float(sys.argv[2])
    startup_file = sys.argv[3] if len(sys.argv) == 4 else None
    port = int(sys.argv[4]) if len(sys.argv) == 5 else 55151

    router = Router(self_ip, update_period, port)

    if startup_file:
        with open(startup_file) as f:
            for line in f:
                parts = line.strip().split()
                if parts and parts[0] == "add":
                    router.add_neighbor(parts[1], int(parts[2]))
                elif parts and parts[0] == "del":
                    router.remove_neighbor(parts[1])

    router.run()


if __name__ == "__main__":
    main()
