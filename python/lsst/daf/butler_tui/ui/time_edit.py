"""Edit box for time.
"""
from __future__ import annotations

#--------------------------------
#  Imports of standard modules --
#--------------------------------
import calendar
from datetime import datetime, timedelta
import logging
import re
from typing import Optional, Tuple

#-----------------------------
# Imports for other modules --
#-----------------------------

#----------------------------------
# Local non-exported definitions --
#----------------------------------

_log = logging.getLogger(__name__)


ABS_TIME_RE = r"""(?P<abs_time>
    (?P<iso>(?P<y>\d+)-(?P<mo>\d+)-(?P<d>\d+)([ T](?P<h>\d+):(?P<m>\d+)(:(?P<s>\d+))?)?)  # iso
    | now | today | yesterday | tomorrow  # some constants
)"""

DELTA_RE = r"""(?P<delta>
    (?P<sign>[-+])
    (?=[ ]*\d)           # Make sure that it is followed by a digit (and not an empty string)
    ([ ]*(?P<d_y>\d+)[ ]*(y|years?))?
    ([ ]*(?P<d_mo>\d+)[ ]*(mo|months?))?
    ([ ]*(?P<d_d>\d+)[ ]*(d|days?))?
    ([ ]*(?P<d_h>\d+)[ ]*(h|hours?))?
    ([ ]*(?P<d_m>\d+)[ ]*(m|min|minutes?))?
    ([ ]*(?P<d_s>\d+)[ ]*(s|sec|seconds?))?
)"""

_re_time_str = re.compile(f"^[ ]*{ABS_TIME_RE}[ ]*{DELTA_RE}?[ ]*$", re.VERBOSE | re.IGNORECASE)
_re_delta_str = re.compile(f"^[ ]*{DELTA_RE}[ ]*$", re.VERBOSE | re.IGNORECASE)


def _parse_time(timestr: str, now: Optional[datetime] = None) -> Tuple[Optional[Tuple], Optional[Tuple]]:
    """Parse time string and return result as two tuples.

    Parameters
    ----------
    timestr : `str`
        String with time representations, possibly empty.
    now : `datetime`, optional
        Time value to use for "now", if not given then `datetime.utcnow()` is
        used.

    Returns
    -------
    absolute : `tuple` or `None`
        It time string contains absolute time in any form then tuple is
        returned containing six integer numbers (year, month, day, hour,
        minute, second). If time string has no absolute time then None is
        returned.
    delta : `tuple` or `None`
        It time string contains delta time in any form then tuple is  returned
        containing six integer numbers (year, month, day, hour, minute,
        second). If time string has no delta time then None is returned.

    Raises
    ------
    ValueError
        Raised if strins is non-blank but cannot be parsed.
    """
    timestr = timestr.strip()
    if not timestr:
        return None, None

    match = _re_delta_str.match(timestr) or _re_time_str.match(timestr)
    if match is None:
        raise ValueError(f"Invalid time value: {timestr}")

    absolute: Optional[Tuple] = None
    delta: Optional[Tuple] = None

    groups = match.groupdict()
    abs_str = groups.get("abs_time")
    if abs_str:
        if groups.get("iso"):
            absolute = tuple(int(groups.get(grp) or 0) for grp in ("y", "mo", "d", "h", "m", "s"))
        else:
            # all times are in UTC
            dt = datetime.utcnow()
            if abs_str == "now":
                absolute = (dt.year, dt.month, dt.day, dt.hour, dt.minute, dt.second)
            elif abs_str == "today":
                absolute = (dt.year, dt.month, dt.day, 0, 0, 0)
            elif abs_str == "yesterday":
                dt -= timedelta(days=-1)
                absolute = (dt.year, dt.month, dt.day, 0, 0, 0)
            elif abs_str == "tomorrow":
                dt -= timedelta(days=1)
                absolute = (dt.year, dt.month, dt.day, 0, 0, 0)
            else:
                raise ValueError(f"Unexpected time value: {abs_str}")

    delta_str = groups.get("delta")
    if delta_str:
        sign = -1 if groups["sign"] == "-" else 1
        delta = tuple(sign * int(groups.get("d_" + grp) or 0) for grp in ("y", "mo", "d", "h", "m", "s"))

    return absolute, delta


def _apply_delta(absolute: Tuple, delta: Optional[Tuple]) -> datetime:
    """Apply delta to time tuple and return resulting datetime.

    Special care is needed when adding months and years, it can lead to
    non-existing dates, e.g. adding one month to Jan 31 will get you Feb 31.
    Current workaround for this is to use last day of the month.

    Parameters
    ----------
    absolute : `tuple`
        Absolute time tuple as returned by `_parse_time`.
    delta : `tuple`, optional
        Deltas tuple as returned by `_parse_time`, None means no deltas.

    Returns
    -------
    dt : `datetime`
        Datetime instance for resulting absolute time.
    """
    td = timedelta(0)
    if delta is not None:
        y, mo, d, h, m, s = absolute
        y += delta[0]
        mo += delta[1]
        while mo > 12:
            mo -= 12
            y += 1
        while mo < 1:
            mo += 12
            y -= 1
        days_in_month = calendar.monthrange(y, mo)[1]
        d = min(d, days_in_month)
        absolute = y, mo, d, h, m, s
        td = timedelta(days=delta[2], hours=delta[3], minutes=delta[4], seconds=delta[5])

    return datetime(*absolute) + td

#------------------------
# Exported definitions --
#------------------------


def combine(since: str, until: str, now: Optional[datetime] = None) -> Tuple[int, int]:
    """Combine two times with optional parts into since/until interval.

    now : `datetime`, optional
        Time value to use for "now", if not given then `datetime.utcnow()` is
        used.
    """

    if now is None:
        now = datetime.utcnow()
    now_tuple = (now.year, now.month, now.day, now.hour, now.minute, now.second)

    time1, delta1 = _parse_time(since, now)
    time2, delta2 = _parse_time(until, now)

    # if both absolute times are missing use "now" if relative time is defined
    if (time1, time2) == (None, None):
        if (delta1, delta2) == (None, None):
            raise ValueError("Both timestamps are empty")
        time1 = now_tuple
        time2 = now_tuple

    dt_since: Optional[datetime] = None
    dt_until: Optional[datetime] = None

    # if an absolute time is defined then adjust for delta
    if time1 is not None:
        dt_since = _apply_delta(time1, delta1)
    if time2 is not None:
        dt_until = _apply_delta(time2, delta2)

    # use otehr time as absolute time if still not defined
    if dt_since is None:
        assert dt_until is not None
        dt_since = _apply_delta(
            (dt_until.year, dt_until.month, dt_until.day, dt_until.hour, dt_until.minute, dt_until.second),
            delta1)
    if dt_until is None:
        assert dt_since is not None
        dt_until = _apply_delta(
            (dt_since.year, dt_since.month, dt_since.day, dt_since.hour, dt_since.minute, dt_since.second),
            delta2)

    epoch = datetime.utcfromtimestamp(0)
    return (
        int((dt_since - epoch).total_seconds()) * 1_000_000_000,
        int((dt_until - epoch).total_seconds()) * 1_000_000_000
    )
