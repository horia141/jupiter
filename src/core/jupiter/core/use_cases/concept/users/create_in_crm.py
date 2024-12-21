# """The command for creating a user in the CRM after the user creation."""
# from jupiter.core.domain.concept.user.user import User


# @async_use_case(User.new_user)
# class UserCreateInCRM(AppAsyncUseCase[User]):
#     """The command for creating a user in the CRM after the user creation."""

#     async def _execute_async(
#         self, args: User, context: AppAsyncUseCaseContext) -> None:
#         """Execute the command's action."""
#         await self._crm.upsert_as_user(args)
