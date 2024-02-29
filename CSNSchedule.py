from CSN import GenerateMissions
from Overrides import CSNSchedule


def Schedule():
    full: bool = False
    # Read Cannon Google Sheet
    schedule: str = CSNSchedule()
    if schedule:
        full = schedule.upper() == 'NEW'
        print(f"Scheduled : {schedule} = {'Full' if full else 'Update'}")
    else:
        print('Nothing Scheduled')
        return None

    GenerateMissions(uselivedata=True, DiscordFullReport=full,
                     DiscordUpdateReport=not full)


if __name__ == '__main__':
    Schedule()
