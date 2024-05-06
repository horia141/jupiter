/* istanbul ignore file */
/* tslint:disable */
/* eslint-disable */
import type { BaseHttpRequest } from './core/BaseHttpRequest';
import type { OpenAPIConfig } from './core/OpenAPI';
import { FetchHttpRequest } from './core/FetchHttpRequest';

import { AuthService } from './services/AuthService';
import { BigPlansService } from './services/BigPlansService';
import { ChoresService } from './services/ChoresService';
import { CoreService } from './services/CoreService';
import { DocsService } from './services/DocsService';
import { GcService } from './services/GcService';
import { GenService } from './services/GenService';
import { GetSummariesService } from './services/GetSummariesService';
import { HabitsService } from './services/HabitsService';
import { InboxTasksService } from './services/InboxTasksService';
import { InitService } from './services/InitService';
import { JournalsService } from './services/JournalsService';
import { LoadProgressReporterTokenService } from './services/LoadProgressReporterTokenService';
import { LoadTopLevelInfoService } from './services/LoadTopLevelInfoService';
import { LoginService } from './services/LoginService';
import { MetricsService } from './services/MetricsService';
import { PersonsService } from './services/PersonsService';
import { ProjectsService } from './services/ProjectsService';
import { PushIntegrationsService } from './services/PushIntegrationsService';
import { ReportService } from './services/ReportService';
import { SearchService } from './services/SearchService';
import { SmartListsService } from './services/SmartListsService';
import { TestHelperService } from './services/TestHelperService';
import { TimePlansService } from './services/TimePlansService';
import { UsersService } from './services/UsersService';
import { VacationsService } from './services/VacationsService';
import { WorkingMemService } from './services/WorkingMemService';
import { WorkspacesService } from './services/WorkspacesService';

type HttpRequestConstructor = new (config: OpenAPIConfig) => BaseHttpRequest;

export class ApiClient {

    public readonly auth: AuthService;
    public readonly bigPlans: BigPlansService;
    public readonly chores: ChoresService;
    public readonly core: CoreService;
    public readonly docs: DocsService;
    public readonly gc: GcService;
    public readonly gen: GenService;
    public readonly getSummaries: GetSummariesService;
    public readonly habits: HabitsService;
    public readonly inboxTasks: InboxTasksService;
    public readonly init: InitService;
    public readonly journals: JournalsService;
    public readonly loadProgressReporterToken: LoadProgressReporterTokenService;
    public readonly loadTopLevelInfo: LoadTopLevelInfoService;
    public readonly login: LoginService;
    public readonly metrics: MetricsService;
    public readonly persons: PersonsService;
    public readonly projects: ProjectsService;
    public readonly pushIntegrations: PushIntegrationsService;
    public readonly report: ReportService;
    public readonly search: SearchService;
    public readonly smartLists: SmartListsService;
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
            VERSION: config?.VERSION ?? '1.0.6',
            WITH_CREDENTIALS: config?.WITH_CREDENTIALS ?? false,
            CREDENTIALS: config?.CREDENTIALS ?? 'include',
            TOKEN: config?.TOKEN,
            USERNAME: config?.USERNAME,
            PASSWORD: config?.PASSWORD,
            HEADERS: config?.HEADERS,
            ENCODE_PATH: config?.ENCODE_PATH,
        });

        this.auth = new AuthService(this.request);
        this.bigPlans = new BigPlansService(this.request);
        this.chores = new ChoresService(this.request);
        this.core = new CoreService(this.request);
        this.docs = new DocsService(this.request);
        this.gc = new GcService(this.request);
        this.gen = new GenService(this.request);
        this.getSummaries = new GetSummariesService(this.request);
        this.habits = new HabitsService(this.request);
        this.inboxTasks = new InboxTasksService(this.request);
        this.init = new InitService(this.request);
        this.journals = new JournalsService(this.request);
        this.loadProgressReporterToken = new LoadProgressReporterTokenService(this.request);
        this.loadTopLevelInfo = new LoadTopLevelInfoService(this.request);
        this.login = new LoginService(this.request);
        this.metrics = new MetricsService(this.request);
        this.persons = new PersonsService(this.request);
        this.projects = new ProjectsService(this.request);
        this.pushIntegrations = new PushIntegrationsService(this.request);
        this.report = new ReportService(this.request);
        this.search = new SearchService(this.request);
        this.smartLists = new SmartListsService(this.request);
        this.testHelper = new TestHelperService(this.request);
        this.timePlans = new TimePlansService(this.request);
        this.users = new UsersService(this.request);
        this.vacations = new VacationsService(this.request);
        this.workingMem = new WorkingMemService(this.request);
        this.workspaces = new WorkspacesService(this.request);
    }
}

