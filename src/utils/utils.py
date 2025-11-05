
def pretty_print(msg: str, *args, sep: str = "-", sep_cnt: int = 15) -> None:
  print(sep * sep_cnt)
  print(msg, *args)
  print(sep * sep_cnt)