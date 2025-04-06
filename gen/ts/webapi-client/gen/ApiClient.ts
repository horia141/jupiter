/* generated using openapi-typescript-codegen -- do not edit */
/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BaseHttpRequest } from './core/BaseHttpRequest';
import type { OpenAPIConfig } from './core/OpenAPI';
import { FetchHttpRequest } from './core/FetchHttpRequest';
import { ActivityService } from './services/ActivityService';
import { ApplicationService } from './services/ApplicationService';
import { AuthService } from './services/AuthService';
import { BigPlansService } from './services/BigPlansService';
import { CalendarService } from './services/CalendarService';
import { ChoresService } from './services/ChoresService';
import { DocsService } from './services/DocsService';
import { EmailService } from './services/EmailService';
import { EntryService } from './services/EntryService';
import { EventFullDaysService } from './services/EventFullDaysService';
import { EventInDayService } from './services/EventInDayService';
import { FullDaysBlockService } from './services/FullDaysBlockService';
import { GcService } from './services/GcService';
import { GenService } from './services/GenService';
import { GetSummariesService } from './services/GetSummariesService';
import { HabitsService } from './services/HabitsService';
import { InboxTasksService } from './services/InboxTasksService';
import { InDayBlockService } from './services/InDayBlockService';
import { ItemService } from './services/ItemService';
import { JournalsService } from './services/JournalsService';
import { LoadProgressReporterTokenService } from './services/LoadProgressReporterTokenService';
import { LoadTopLevelInfoService } from './services/LoadTopLevelInfoService';
import { LoginService } from './services/LoginService';
import { MetricsService } from './services/MetricsService';
import { NotesService } from './services/NotesService';
import { PersonsService } from './services/PersonsService';
import { ProjectsService } from './services/ProjectsService';
import { ScheduleService } from './services/ScheduleService';
import { SlackService } from './services/SlackService';
import { SmartListsService } from './services/SmartListsService';
import { StreamService } from './services/StreamService';
import { TagService } from './services/TagService';
import { TestHelperService } from './services/TestHelperService';
import { TimePlansService } from './services/TimePlansService';
import { UsersService } from './services/UsersService';
import { VacationsService } from './services/VacationsService';
import { WorkingMemService } from './services/WorkingMemService';
import { WorkspacesService } from './services/WorkspacesService';
type HttpRequestConstructor = new (config: OpenAPIConfig) => BaseHttpRequest;
export class ApiClient {
    public readonly activity: ActivityService;
    public readonly application: ApplicationService;
    public readonly auth: AuthService;
    public readonly bigPlans: BigPlansService;
    public readonly calendar: CalendarService;
    public readonly chores: ChoresService;
    public readonly docs: DocsService;
    public readonly email: EmailService;
    public readonly entry: EntryService;
    public readonly eventFullDays: EventFullDaysService;
    public readonly eventInDay: EventInDayService;
    public readonly fullDaysBlock: FullDaysBlockService;
    public readonly gc: GcService;
    public readonly gen: GenService;
    public readonly getSummaries: GetSummariesService;
    public readonly habits: HabitsService;
    public readonly inboxTasks: InboxTasksService;
    public readonly inDayBlock: InDayBlockService;
    public readonly item: ItemService;
    public readonly journals: JournalsService;
    public readonly loadProgressReporterToken: LoadProgressReporterTokenService;
    public readonly loadTopLevelInfo: LoadTopLevelInfoService;
    public readonly login: LoginService;
    public readonly metrics: MetricsService;
    public readonly notes: NotesService;
    public readonly persons: PersonsService;
    public readonly projects: ProjectsService;
    public readonly schedule: ScheduleService;
    public readonly slack: SlackService;
    public readonly smartLists: SmartListsService;
    public readonly stream: StreamService;
    public readonly tag: TagService;
    public readonly testHelper: TestHelperService;
    public readonly timePlans: TimePlansService;
    public readonly users: UsersService;
    public readonly vacations: VacationsService;
    public readonly workingMem: WorkingMemService;
    public readonly workspaces: WorkspacesService;
    public readonly request: BaseHttpRequest;
    constructor(config?: Partial<OpenAPIConfig>, HttpRequest: HttpRequestConstructor = FetchHttpRequest) {
        this.request = new HttpRequest({
            BASE: config?.BASE ?? '',
            VERSION: config?.VERSION ?? '1.1.4',
            WITH_CREDENTIALS: config?.WITH_CREDENTIALS ?? false,
            CREDENTIALS: config?.CREDENTIALS ?? 'include',
            TOKEN: config?.TOKEN,
            USERNAME: config?.USERNAME,
            PASSWORD: config?.PASSWORD,
            HEADERS: config?.HEADERS,
            ENCODE_PATH: config?.ENCODE_PATH,
        });
        this.activity = new ActivityService(this.request);
        this.application = new ApplicationService(this.request);
        this.auth = new AuthService(this.request);
        this.bigPlans = new BigPlansService(this.request);
        this.calendar = new CalendarService(this.request);
        this.chores = new ChoresService(this.request);
        this.docs = new DocsService(this.request);
        this.email = new EmailService(this.request);
        this.entry = new EntryService(this.request);
        this.eventFullDays = new EventFullDaysService(this.request);
        this.eventInDay = new EventInDayService(this.request);
        this.fullDaysBlock = new FullDaysBlockService(this.request);
        this.gc = new GcService(this.request);
        this.gen = new GenService(this.request);
        this.getSummaries = new GetSummariesService(this.request);
        this.habits = new HabitsService(this.request);
        this.inboxTasks = new InboxTasksService(this.request);
        this.inDayBlock = new InDayBlockService(this.request);
        this.item = new ItemService(this.request);
        this.journals = new JournalsService(this.request);
        this.loadProgressReporterToken = new LoadProgressReporterTokenService(this.request);
        this.loadTopLevelInfo = new LoadTopLevelInfoService(this.request);
        this.login = new LoginService(this.request);
        this.metrics = new MetricsService(this.request);
        this.notes = new NotesService(this.request);
        this.persons = new PersonsService(this.request);
        this.projects = new ProjectsService(this.request);
        this.schedule = new ScheduleService(this.request);
        this.slack = new SlackService(this.request);
        this.smartLists = new SmartListsService(this.request);
        this.stream = new StreamService(this.request);
        this.tag = new TagService(this.request);
        this.testHelper = new TestHelperService(this.request);
        this.timePlans = new TimePlansService(this.request);
        this.users = new UsersService(this.request);
        this.vacations = new VacationsService(this.request);
        this.workingMem = new WorkingMemService(this.request);
        this.workspaces = new WorkspacesService(this.request);
    }
}

