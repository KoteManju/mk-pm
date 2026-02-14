from app.schemas import TaskStatus

print('Schema TaskStatus members:')
for member in TaskStatus:
    print(f'  {member.name} = {member.value}')
