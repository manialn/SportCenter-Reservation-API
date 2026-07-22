class CacheKeys:

    @staticmethod
    def facilities(
    page: int,
    page_size: int,
    search: str | None,
    facility_type: str | None,
    ) -> str:
        return (
            f"facilities:{page}:{page_size}:"
            f"{search or 'all'}:{facility_type or 'all'}"
        )

    @staticmethod
    def facility(facility_id: str) -> str:
        return f"facility:{facility_id}"

    @staticmethod
    def facility_schedule(facility_id: str) -> str:
        return f"facility_schedule:{facility_id}"

    @staticmethod
    def timeslots(
        facility_id: str,
        date: str,
        page: int,
        page_size: int,
    ):
        return f"timeslots:{facility_id}:{date}:{page}:{page_size}"


cache_keys = CacheKeys()