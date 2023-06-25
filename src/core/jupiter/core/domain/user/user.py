"""A user of Jupiter."""
from dataclasses import dataclass

from jupiter.core.domain.email_address import EmailAddress
from jupiter.core.domain.timezone import Timezone
from jupiter.core.domain.user.avatar import Avatar
from jupiter.core.domain.user.user_name import UserName
from jupiter.core.framework.base.entity_id import BAD_REF_ID
from jupiter.core.framework.base.timestamp import Timestamp
from jupiter.core.framework.entity import FIRST_VERSION, Entity, RootEntity
from jupiter.core.framework.event import EventSource
from jupiter.core.framework.update_action import UpdateAction


@dataclass
class User(RootEntity):
    """A user of Jupiter."""

    @dataclass
    class Created(Entity.Created):
        """Created event."""

    @dataclass
    class Update(Entity.Updated):
        """Updated event."""

    email_address: EmailAddress
    name: UserName
    avatar: Avatar
    timezone: Timezone

    @staticmethod
    def new_user(
        email_address: EmailAddress,
        name: UserName,
        timezone: Timezone,
        source: EventSource,
        created_time: Timestamp,
    ) -> "User":
        """Create a new user."""
        user = User(
            ref_id=BAD_REF_ID,
            version=FIRST_VERSION,
            archived=False,
            created_time=created_time,
            last_modified_time=created_time,
            archived_time=None,
            events=[
                User.Created.make_event_from_frame_args(
                    source, FIRST_VERSION, created_time
                ),
            ],
            email_address=email_address,
            name=name,
            avatar=Avatar.from_user_name(name),
            timezone=timezone,
        )

        return user

    def update(
        self,
        name: UpdateAction[UserName],
        timezone: UpdateAction[Timezone],
        source: EventSource,
        modification_time: Timestamp,
    ) -> "User":
        """Update properties of the user."""
        return self._new_version(
            name=name.or_else(self.name),
            avatar=name.transform(lambda n: Avatar.from_user_name(n)).or_else(
                self.avatar
            ),
            timezone=timezone.or_else(self.timezone),
            new_event=User.Update.make_event_from_frame_args(
                source, self.version, modification_time
            ),
        )
